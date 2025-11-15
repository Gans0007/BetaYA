from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_pool
from datetime import datetime
from services.user_service import recalculate_total_confirmed_days
from services.user_service import update_user_streak
from services.xp_service import add_xp_for_confirmation, check_next_league

import pytz

router = Router()


# -------------------------------
# 🔹 FSM состояния
# -------------------------------
class ConfirmHabitFSM(StatesGroup):
    waiting_for_media = State()


# -------------------------------
# 🔹 Кнопка отмены
# -------------------------------
def cancel_kb(habit_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_media_{habit_id}")]]
    )


# -------------------------------
# 🔹 Кнопки "Подтвердить" / "Удалить"
# -------------------------------
async def get_habit_buttons(habit_id: int, user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:

        user_row = await conn.fetchrow("SELECT timezone FROM users WHERE user_id=$1", user_id)
        user_tz = user_row["timezone"] if user_row and user_row["timezone"] else "Europe/Kyiv"
        user_timezone = pytz.timezone(user_tz)
        user_now = datetime.now(user_timezone)

        habit = await conn.fetchrow("""
            SELECT done_days, days, is_challenge
            FROM habits
            WHERE id=$1
        """, habit_id)

        if not habit:
            return InlineKeyboardMarkup(inline_keyboard=[])

        done_days = habit["done_days"]
        total_days = habit["days"]
        is_challenge = habit["is_challenge"]

        # ---------------- ЧЕЛЛЕНДЖ ----------------
        if is_challenge:
            if done_days >= total_days:
                return InlineKeyboardMarkup(inline_keyboard=[])

            row = await conn.fetchrow("""
                SELECT datetime FROM confirmations
                WHERE user_id=$1 AND habit_id=$2
                ORDER BY datetime DESC LIMIT 1
            """, user_id, habit_id)

            button_text = "✅ Подтвердить"
            if row:
                last_time = row["datetime"].astimezone(user_timezone)
                if last_time.date() == user_now.date():
                    button_text = "♻️ Переподтвердить"

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=button_text, callback_data=f"confirm_{habit_id}"),
                        InlineKeyboardButton(text="🗑 Удалить", callback_data=f"ask_delete_{habit_id}")
                    ]
                ]
            )
            return keyboard

        # ---------------- ПРИВЫЧКА ----------------
        if done_days >= total_days:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="🔁 Продлить", callback_data=f"extend_{habit_id}"),
                        InlineKeyboardButton(text="✅ Завершить", callback_data=f"finish_{habit_id}")
                    ]
                ]
            )
            return keyboard

        row = await conn.fetchrow("""
            SELECT datetime FROM confirmations
            WHERE user_id=$1 AND habit_id=$2
            ORDER BY datetime DESC LIMIT 1
        """, user_id, habit_id)

        button_text = "✅ Подтвердить"
        if row:
            last_time = row["datetime"].astimezone(user_timezone)
            if last_time.date() == user_now.date():
                button_text = "♻️ Переподтвердить"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=button_text, callback_data=f"confirm_{habit_id}"),
                    InlineKeyboardButton(text="🗑 Удалить", callback_data=f"ask_delete_{habit_id}")
                ]
            ]
        )

    return keyboard

# -------------------------------
# 🔹 Обработка "Подтвердить"
# -------------------------------
@router.callback_query(F.data.startswith("confirm_"))
async def confirm_habit_start(callback: types.CallbackQuery, state: FSMContext):
    habit_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    pool = await get_pool()
    async with pool.acquire() as conn:

        user_row = await conn.fetchrow("SELECT timezone FROM users WHERE user_id=$1", user_id)
        user_tz = user_row["timezone"] if user_row and user_row["timezone"] else "Europe/Kyiv"
        user_timezone = pytz.timezone(user_tz)
        user_now = datetime.now(user_timezone)

        habit_row = await conn.fetchrow("""
            SELECT name, is_challenge
            FROM habits
            WHERE id=$1
        """, habit_id)

        if not habit_row:
            await callback.answer("❌ Привычка не найдена.", show_alert=True)
            return

        habit_name = habit_row["name"]
        is_challenge = habit_row["is_challenge"]

        habit_title = f"челленджа *{habit_name}*" if is_challenge else f"привычки *{habit_name}*"

        row = await conn.fetchrow("""
            SELECT datetime FROM confirmations
            WHERE user_id=$1 AND habit_id=$2
            ORDER BY datetime DESC LIMIT 1
        """, user_id, habit_id)

        if row:
            last_time = row["datetime"].astimezone(user_timezone)
            if last_time.date() == user_now.date():
                await state.update_data(habit_id=habit_id, reverify=True)
                await state.set_state(ConfirmHabitFSM.waiting_for_media)

                await callback.message.answer(
                    f"♻️ Сегодня уже подтверждено.\n"
                    f"Пришли новое фото/видео, чтобы *переподтвердить* {habit_title}.",
                    parse_mode="Markdown",
                    reply_markup=cancel_kb(habit_id)
                )
                await callback.answer()
                return

        await state.update_data(habit_id=habit_id, reverify=False)
        await state.set_state(ConfirmHabitFSM.waiting_for_media)

        await callback.message.answer(
            f"📸 Пришли фото, видео или кружочек для подтверждения {habit_title} 💪",
            parse_mode="Markdown",
            reply_markup=cancel_kb(habit_id)
        )

    await callback.answer()



# -------------------------------
# 🔹 Отмена во время ожидания медиа
# -------------------------------
@router.callback_query(F.data.startswith("cancel_media_"))
async def cancel_media(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❎ Подтверждение отменено.")
    await callback.answer()



# -------------------------------
# 🔹 Получаем медиафайл
# -------------------------------
@router.message(ConfirmHabitFSM.waiting_for_media)
async def receive_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    habit_id = data.get("habit_id")
    reverify = data.get("reverify", False)
    user_id = message.from_user.id

    pool = await get_pool()
    file_id = None
    file_type = None

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

    async with pool.acquire() as conn:

        habit_exists = await conn.fetchval("SELECT COUNT(*) FROM habits WHERE id=$1", habit_id)
        if habit_exists == 0:
            await message.answer("⚠️ Эта привычка уже завершена.")
            await state.clear()
            return

        if reverify:
            await conn.execute("""
                UPDATE confirmations
                SET file_id=$1, file_type=$2, datetime=NOW()
                WHERE user_id=$3 AND habit_id=$4
            """, file_id, file_type, user_id, habit_id)

            await message.answer("♻️ Переподтверждение обновлено 💪")

        else:
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

            await message.answer(
                f"✨ +{xp_gain} XP\n"
                f"✅ Привычка подтверждена! Так держать 💪"
            )

        # -------------------------------------------------------------------------
        # 🔥 Автозавершение челленджа при выполнении требуемых дней
        # -------------------------------------------------------------------------
        habit = await conn.fetchrow("""
            SELECT user_id, name, days, done_days, is_challenge, challenge_id
            FROM habits WHERE id=$1
        """, habit_id)

        if habit and habit["is_challenge"] and habit["done_days"] >= habit["days"]:

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

            # Счётчик завершённых челленджей
            await conn.execute("""
                UPDATE users SET finished_challenges = finished_challenges + 1 WHERE user_id=$1
            """, habit["user_id"])

            # Добавляем звёзды
            if existing:
                stars_gained = new_count - existing["repeat_count"]
            else:
                stars_gained = 1

            await conn.execute("""
                UPDATE users SET total_stars = total_stars + $1 WHERE user_id=$2
            """, stars_gained, habit["user_id"])

            # Удаляем челлендж из активных
            await conn.execute("DELETE FROM habits WHERE id=$1", habit_id)

            stars_display = "⭐" * stars + "☆" * (3 - stars)

            await message.answer(
                f"🔥 Челлендж *{habit['name']}* завершён!\n"
                f"🏆 Результат: {stars_display}\n\n"
                f"Продолжай в том же духе 💪",
                parse_mode="Markdown"
            )

    await state.clear()

# -------------------------------
# 🔹 Шаг 1: Запрос подтверждения удаления
# -------------------------------
@router.callback_query(F.data.startswith("ask_delete_"))
async def ask_delete_confirmation(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"delete_habit_{habit_id}"),
                InlineKeyboardButton(text="❌ Нет", callback_data="cancel_delete")
            ]
        ]
    )

    await callback.message.edit_text(
        "⚠️ Если ты удалишь привычку, весь прогресс будет потерян.\n\n"
        "Ты уверен, что хочешь удалить её?",
        reply_markup=keyboard
    )
    await callback.answer()


# -------------------------------
# 🔹 Шаг 2: Удаление привычки + логика вывода списка
# -------------------------------
@router.callback_query(F.data.startswith("delete_habit_"))
async def delete_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    pool = await get_pool()

    # Удаляем подтверждения и саму привычку
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM confirmations WHERE habit_id = $1", habit_id)
        await conn.execute("DELETE FROM habits WHERE id = $1", habit_id)

        # Узнаём, сколько осталось привычек
        rows = await conn.fetch("""
            SELECT id, name, is_challenge
            FROM habits
            WHERE user_id = $1 AND is_active = TRUE
        """, user_id)

    count = len(rows)

    # 1) Если не осталось привычек
    if count == 0:
        await callback.message.edit_text(
            "😴 У тебя пока нет активных привычек или челленджей."
        )
        await callback.answer("🗑 Привычка удалена.")
        return

    # 2) Если осталось 1 или 2
    if count <= 2:
        await callback.message.edit_text("🗑 Привычка удалена.")
        await callback.answer()
        return

    # 3) Если осталось 3+
    from handlers.active_tasks_handler import build_active_list
    text, kb, _ = await build_active_list(user_id)

    await callback.message.edit_text(
        text, parse_mode="Markdown", reply_markup=kb
    )
    await callback.answer("🗑 Привычка удалена.")


# -------------------------------
# 🔹 Отмена удаления
# -------------------------------
@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    from handlers.active_tasks_handler import build_active_list

    text, kb, rows = await build_active_list(user_id)

    if not rows:
        await callback.message.edit_text("😴 У тебя пока нет активных привычек или челленджей.")
    else:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)

    await callback.answer("Отмена удаления.")


# -------------------------------
# 🔹 Продление привычки
# -------------------------------
@router.callback_query(F.data.regexp(r"^extend_\d+$"))
async def extend_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[1])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"extend_yes_{habit_id}"),
                InlineKeyboardButton(text="❌ Нет", callback_data="extend_no")
            ]
        ]
    )

    await callback.message.edit_text(
        "🔁 Хочешь продлить привычку на 5 дней?",
        reply_markup=keyboard
    )
    await callback.answer()


# -------------------------------
# 🔹 Продление привычки (Да)
# -------------------------------
@router.callback_query(F.data.regexp(r"^extend_yes_\d+$"))
async def extend_habit_yes(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    pool = await get_pool()

    async with pool.acquire() as conn:

        await conn.execute("""
            UPDATE habits
            SET days = days + 5
            WHERE id = $1
        """, habit_id)

        habit = await conn.fetchrow("""
            SELECT h.id, h.name, h.description, h.days, h.done_days, h.is_challenge, h.difficulty,
                   (SELECT datetime FROM confirmations WHERE habit_id = h.id ORDER BY datetime DESC LIMIT 1) AS last_date,
                   u.timezone
            FROM habits h
            JOIN users u ON u.user_id = h.user_id
            WHERE h.id=$1 AND h.user_id=$2
        """, habit_id, user_id)

    if not habit:
        await callback.message.edit_text("❌ Привычка не найдена или уже завершена.")
        await callback.answer()
        return

    from handlers.active_tasks_handler import send_habit_card

    await callback.message.delete()
    await send_habit_card(callback.message, habit, user_id)

    await callback.answer("🔁 Привычка продлена на 5 дней!")


# -------------------------------
# 🔹 Продление привычки (Нет)
# -------------------------------
@router.callback_query(F.data == "extend_no")
async def extend_habit_no(callback: types.CallbackQuery):
    await callback.message.edit_text("❎ Продление отменено.")
    await callback.answer()


# -------------------------------
# 🔹 Завершение привычки
# -------------------------------
@router.callback_query(F.data.regexp(r"^finish_\d+$"))
async def finish_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[1])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"finish_yes_{habit_id}"),
                InlineKeyboardButton(text="❌ Нет", callback_data="finish_no")
            ]
        ]
    )

    await callback.message.edit_text(
        "🏁 Завершить привычку и добавить в статистику?",
        reply_markup=keyboard
    )
    await callback.answer()


# -------------------------------
# 🔹 Завершение привычки (ДА)
# -------------------------------
@router.callback_query(F.data.regexp(r"^finish_yes_\d+$"))
async def finish_habit_yes(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    pool = await get_pool()

    # Увеличиваем статистику
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET finished_habits = finished_habits + 1
            WHERE user_id=$1
        """, user_id)

        habit = await conn.fetchrow("""
            DELETE FROM habits
            WHERE id=$1
            RETURNING name
        """, habit_id)

    name = habit["name"] if habit else "Привычка"

    from handlers.active_tasks_handler import build_active_list
    text, kb, rows = await build_active_list(user_id)

    if not rows:
        await callback.message.edit_text(
            f"✅ {name} завершена!\n\nТеперь у тебя нет активных привычек."
        )
    else:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)

    await callback.answer("🎉 Привычка завершена!")


# -------------------------------
# 🔹 Завершение привычки (НЕТ)
# -------------------------------
@router.callback_query(F.data == "finish_no")
async def finish_habit_no(callback: types.CallbackQuery):
    await callback.message.edit_text("❎ Завершение отменено.")
    await callback.answer()

