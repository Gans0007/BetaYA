from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_pool
from datetime import datetime
import pytz

router = Router()

# -------------------------------
# 🔹 FSM состояния
# -------------------------------
class ConfirmHabitFSM(StatesGroup):
    waiting_for_media = State()


# -------------------------------
# 🔹 Кнопки "Подтвердить" / "Удалить" (динамические)
# -------------------------------
async def get_habit_buttons(habit_id: int, user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        user_row = await conn.fetchrow("SELECT timezone FROM users WHERE user_id = $1", user_id)
        user_tz = user_row["timezone"] if user_row and user_row["timezone"] else "Europe/Kyiv"
        user_timezone = pytz.timezone(user_tz)
        user_now = datetime.now(user_timezone)

        row = await conn.fetchrow("""
            SELECT datetime FROM confirmations
            WHERE user_id = $1 AND habit_id = $2
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
        user_row = await conn.fetchrow("SELECT timezone FROM users WHERE user_id = $1", user_id)
        user_tz = user_row["timezone"] if user_row and user_row["timezone"] else "Europe/Kyiv"
        user_timezone = pytz.timezone(user_tz)
        user_now = datetime.now(user_timezone)

        row = await conn.fetchrow("""
            SELECT id, datetime FROM confirmations
            WHERE user_id = $1 AND habit_id = $2
            ORDER BY datetime DESC LIMIT 1
        """, user_id, habit_id)

        if row:
            last_time = row["datetime"].astimezone(user_timezone)
            if last_time.date() == user_now.date():
                await state.update_data(habit_id=habit_id, reverify=True)
                await state.set_state(ConfirmHabitFSM.waiting_for_media)
                await callback.message.answer(
                    "♻️ Ты уже подтверждал сегодня.\n"
                    "Пришли новое фото/видео, чтобы *переподтвердить* привычку."
                )
                await callback.answer()
                return

        await state.update_data(habit_id=habit_id, reverify=False)
        await state.set_state(ConfirmHabitFSM.waiting_for_media)
        await callback.message.answer(
            "📸 Пришли фото, видео или кружочек, подтверждающий выполнение привычки 💪"
        )

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
        await message.answer("⚠️ Нужно отправить фото, видео или кружочек 🎥")
        return

    async with pool.acquire() as conn:
        if reverify:
            await conn.execute("""
                UPDATE confirmations
                SET file_id = $1, file_type = $2, datetime = NOW()
                WHERE user_id = $3 AND habit_id = $4
            """, file_id, file_type, user_id, habit_id)

            await message.answer("♻️ Видео обновлено. Переподтверждение сохранено 💪")

        else:
            await conn.execute("""
                INSERT INTO confirmations (user_id, habit_id, datetime, file_id, file_type, confirmed)
                VALUES ($1, $2, NOW(), $3, $4, TRUE)
            """, user_id, habit_id, file_id, file_type)

            await conn.execute("""
                UPDATE habits
                SET done_days = done_days + 1
                WHERE id = $1
            """, habit_id)

            await message.answer("✅ Привычка подтверждена! Отличная работа 💪")

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
# 🔹 Шаг 2: Подтверждение удаления
# -------------------------------
@router.callback_query(F.data.startswith("delete_habit_"))
async def delete_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM confirmations WHERE habit_id = $1", habit_id)
        await conn.execute("DELETE FROM habits WHERE id = $1", habit_id)

    await callback.message.edit_text("🗑 Привычка удалена вместе с прогрессом.")
    await callback.answer()


# -------------------------------
# 🔹 Шаг 3: Отмена удаления
# -------------------------------
@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: types.CallbackQuery):
    # Восстанавливаем карточку привычки
    # Получаем habit_id из текста предыдущего сообщения
    # (из callback'а перед этим — ask_delete_confirmation)
    message_text = callback.message.text

    # Пробуем извлечь ID привычки из предыдущего callback_data
    # (берем из inline-кнопок, если они остались)
    keyboard = callback.message.reply_markup
    habit_id = None

    if keyboard and keyboard.inline_keyboard:
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data and button.callback_data.startswith("delete_habit_"):
                    habit_id = int(button.callback_data.split("_")[2])
                    break

    if not habit_id:
        await callback.message.edit_text("❎ Ошибка восстановления карточки.")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        habit = await conn.fetchrow("""
            SELECT name, description, days, done_days
            FROM habits
            WHERE id = $1
        """, habit_id)

    if habit:
        name = habit["name"]
        desc = habit["description"]
        total_days = habit["days"]
        done = habit["done_days"]
        progress = int((done / total_days) * 100) if total_days > 0 else 0

        text = (
            f"🏁 {name}\n\n"
            f"📖 {desc}\n\n"
            f"📅 Прогресс: {done} из {total_days} дней ({progress}%)"
        )

        keyboard = await get_habit_buttons(habit_id, callback.from_user.id)
        await callback.message.edit_text(text, reply_markup=keyboard)
    else:
        await callback.message.edit_text("❎ Привычка не найдена.")

    await callback.answer()

