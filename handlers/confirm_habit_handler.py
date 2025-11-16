from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import pytz

from database import get_pool

from services.user_service import recalculate_total_confirmed_days
from services.user_service import update_user_streak
from services.xp_service import add_xp_for_confirmation

from services.habit_view_service import send_habit_card, build_active_list

router = Router()


# ================================
# 🔹 FSM состояния
# ================================
class ConfirmHabitFSM(StatesGroup):
    waiting_for_media = State()


# ================================
# 🔹 Кнопка отмены
# ================================
def cancel_kb(habit_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_media_{habit_id}")]
        ]
    )


# ================================
# 🔹 Старт подтверждения
# ================================
@router.callback_query(F.data.startswith("confirm_"))
async def confirm_habit_start(callback: types.CallbackQuery, state: FSMContext):
    habit_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    pool = await get_pool()
    async with pool.acquire() as conn:
        user_row = await conn.fetchrow(
            "SELECT timezone FROM users WHERE user_id=$1",
            user_id
        )
        user_tz = user_row["timezone"] if user_row else "Europe/Kyiv"
        tz = pytz.timezone(user_tz)
        now = datetime.now(tz)

        habit = await conn.fetchrow("""
            SELECT name, is_challenge
            FROM habits
            WHERE id=$1
        """, habit_id)

        if not habit:
            await callback.answer("❌ Привычка не найдена.", show_alert=True)
            return

        habit_name = habit["name"]
        is_challenge = habit["is_challenge"]

        title = f"челленджа *{habit_name}*" if is_challenge else f"привычки *{habit_name}*"

        # Проверяем, было ли подтверждение сегодня
        last = await conn.fetchrow("""
            SELECT datetime FROM confirmations
            WHERE user_id=$1 AND habit_id=$2
            ORDER BY datetime DESC LIMIT 1
        """, user_id, habit_id)

        if last:
            last_dt = last["datetime"].astimezone(tz)
            if last_dt.date() == now.date():
                # Reverify
                await state.update_data(habit_id=habit_id, reverify=True)
                await state.set_state(ConfirmHabitFSM.waiting_for_media)

                await callback.message.answer(
                    f"♻️ Уже есть подтверждение сегодня.\n"
                    f"Пришли новое медиа, чтобы *переподтвердить* {title}.",
                    parse_mode="Markdown",
                    reply_markup=cancel_kb(habit_id)
                )
                await callback.answer()
                return

        # Обычное подтверждение
        await state.update_data(habit_id=habit_id, reverify=False)
        await state.set_state(ConfirmHabitFSM.waiting_for_media)

        await callback.message.answer(
            f"📸 Пришли фото, видео или кружочек для подтверждения {title} 💪",
            parse_mode="Markdown",
            reply_markup=cancel_kb(habit_id)
        )

    await callback.answer()


# ================================
# 🔹 Отмена подтверждения
# ================================
@router.callback_query(F.data.startswith("cancel_media_"))
async def cancel_media(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❎ Подтверждение отменено.")
    await callback.answer()


# ================================
# 🔹 Получаем медиафайл
# ================================
@router.message(ConfirmHabitFSM.waiting_for_media)
async def receive_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    habit_id = data["habit_id"]
    reverify = data["reverify"]
    user_id = message.from_user.id

    # Определяем тип медиа
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.video_note:
        file_id = message.video_note.file_id
        file_type = "circle"
    else:
        await message.answer("⚠️ Нужно фото, видео или кружочек 🎥")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:

        # Проверяем, существует ли ещё привычка
        exists = await conn.fetchval("SELECT COUNT(*) FROM habits WHERE id=$1", habit_id)
        if exists == 0:
            await message.answer("⚠️ Эта привычка уже завершена.")
            await state.clear()
            return

        # =============================
        # ♻️ REVERIFY
        # =============================
        if reverify:
            await conn.execute("""
                UPDATE confirmations
                SET file_id=$1, file_type=$2, datetime=NOW()
                WHERE user_id=$3 AND habit_id=$4
            """, file_id, file_type, user_id, habit_id)

            await message.answer("♻️ Переподтверждение обновлено 💪")

        else:
            # =============================
            # ✔ Новое подтверждение
            # =============================
            await conn.execute("""
                INSERT INTO confirmations (user_id, habit_id, datetime, file_id, file_type, confirmed)
                VALUES ($1, $2, NOW(), $3, $4, TRUE)
            """, user_id, habit_id, file_id, file_type)

            await update_user_streak(user_id)
            xp_gain = await add_xp_for_confirmation(user_id, habit_id)

            await conn.execute("""
                UPDATE habits
                SET done_days = done_days + 1
                WHERE id=$1
            """, habit_id)

            await recalculate_total_confirmed_days(user_id)

            await message.answer(f"✨ +{xp_gain} XP\n✅ Готово! Продолжаем 💪")

        # =============================
        # 🔥 Проверка автозавершения челленджа
        # =============================
        habit = await conn.fetchrow("""
            SELECT user_id, name, days, done_days, is_challenge, challenge_id
            FROM habits WHERE id=$1
        """, habit_id)

        if not habit:
            await state.clear()
            return

        if habit["is_challenge"] and habit["done_days"] >= habit["days"]:

            # Получаем уже существующий прогресс по челленджу
            existing = await conn.fetchrow("""
                SELECT repeat_count FROM completed_challenges
                WHERE user_id=$1 AND challenge_id=$2
            """, habit["user_id"], habit["challenge_id"])

            if existing:
                new_count = min(existing["repeat_count"] + 1, 3)
                await conn.execute("""
                    UPDATE completed_challenges
                    SET repeat_count=$1, completed_at=NOW()
                    WHERE user_id=$2 AND challenge_id=$3
                """, new_count, habit["user_id"], habit["challenge_id"])
                stars = new_count
            else:
                await conn.execute("""
                    INSERT INTO completed_challenges (user_id, challenge_name, level_key, challenge_id, repeat_count)
                    VALUES ($1, $2, 'auto', $3, 1)
                """, habit["user_id"], habit["name"], habit["challenge_id"])
                stars = 1

            # Статистика
            await conn.execute("""
                UPDATE users 
                SET finished_challenges = finished_challenges + 1,
                    total_stars = total_stars + $1
                WHERE user_id=$2
            """, 1 if not existing else stars - existing["repeat_count"], habit["user_id"])

            # Удаляем челлендж из активных
            await conn.execute("DELETE FROM habits WHERE id=$1", habit_id)

            stars_display = "⭐" * stars + "☆" * (3 - stars)

            await message.answer(
                f"🔥 Челлендж *{habit['name']}* завершён!\n"
                f"🏆 Результат: {stars_display}\n\n"
                f"Продолжаем доминировать 💪",
                parse_mode="Markdown"
            )

    await state.clear()


# ================================
# 🔥 1) Запрос подтверждения удаления привычки
#     Срабатывает по кнопке ask_delete_<id>
# ================================
@router.callback_query(F.data.startswith("ask_delete_"))
async def ask_delete(callback: types.CallbackQuery):
    # Получаем id привычки
    habit_id = int(callback.data.split("_")[2])

    # Клавиатура: Да / Отмена
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Да, удалить", callback_data=f"delete_habit_{habit_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="dismiss_delete")]
        ]
    )

    # Показываем вопрос
    await callback.message.edit_text(
        "❗ Ты точно хочешь удалить эту привычку?",
        reply_markup=kb
    )

    await callback.answer()



# ================================
# 🔥 2) Удаление привычки
#     Срабатывает по кнопке delete_habit_<id>
# ================================
@router.callback_query(F.data.startswith("delete_habit_"))
async def delete_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    pool = await get_pool()
    async with pool.acquire() as conn:

        # 1) Удаляем подтверждения этой привычки
        await conn.execute(
            "DELETE FROM confirmations WHERE habit_id=$1",
            habit_id
        )

        # 2) Удаляем саму привычку
        await conn.execute(
            "DELETE FROM habits WHERE id=$1 AND user_id=$2",
            habit_id, user_id
        )

        # 3) Получаем оставшиеся привычки после удаления
        habits = await conn.fetch("""
            SELECT h.id, h.name, h.description, h.days, h.done_days, h.is_challenge,
                   h.difficulty,
                   (SELECT datetime FROM confirmations
                        WHERE habit_id=h.id
                        ORDER BY datetime DESC LIMIT 1) AS last_date,
                   u.timezone
            FROM habits h
            JOIN users u ON u.user_id=h.user_id
            WHERE h.user_id=$1 AND h.is_active=TRUE
            ORDER BY h.is_challenge DESC, h.created_at DESC
        """, user_id)

    # === 0 привычек: просто выводим текст ===
    if not habits:
        await callback.message.edit_text("🗑 Привычка удалена.\n\n😴 Больше нет активных привычек.")
        await callback.answer()
        return

    chat = callback.message.chat  # запоминаем чат для отправки сообщений

    # === 1–2 привычки: показываем их как карточки ===
    if len(habits) <= 2:
        # Сначала сообщаем об удалении
        await callback.message.edit_text("🗑 Привычка удалена.")

        # Выводим оставшиеся карточки
        for habit in habits:
            await send_habit_card(chat, habit, user_id)

        await callback.answer()
        return

    # === 3+ привычек: показываем список ===
    text, kb, _ = await build_active_list(user_id)

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=kb
    )

    await callback.answer("🗑 Привычка удалена.")


# ================================
# 🔥 3) Отмена удаления привычки
# ================================
@router.callback_query(F.data == "dismiss_delete")
async def dismiss_delete(callback: types.CallbackQuery):
    # Возвращаем обычное сообщение
    await callback.message.edit_text("Отменено ❎")
    await callback.answer()



