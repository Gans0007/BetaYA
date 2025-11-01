import pytz
from datetime import datetime
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import get_pool

router = Router()


# -------------------------------
# 🔹 Главное меню
# -------------------------------
def main_menu_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="📋 Активные задания")],
        [KeyboardButton(text="🏆 Рейтинг"), KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="➕ Добавить привычку / челлендж")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Выбери действие…",
    )


# -------------------------------
# 🔹 Команда /start
# -------------------------------
@router.message(CommandStart())
async def start_command(message: types.Message):
    # Определяем часовой пояс пользователя
    user_timezone = "Europe/Kyiv"  # по умолчанию
    if message.from_user and message.from_user.language_code == "en":
        user_timezone = "Europe/London"
    elif message.from_user and message.from_user.language_code == "uk":
        user_timezone = "Europe/Kyiv"
    elif message.from_user and message.from_user.language_code == "ru":
        user_timezone = "Europe/Moscow"

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (user_id, username, first_name, timezone)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) DO UPDATE
              SET username = EXCLUDED.username,
                  first_name = EXCLUDED.first_name,
                  timezone = EXCLUDED.timezone
            """,
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            user_timezone,
        )

    text = (
        "Привет! ✌️ Я Your Ambitions бот.\n\n"
        "Здесь ты можешь добавлять привычки, брать челленджи и следить за прогрессом.\n"
        "Теперь я запомнил твой часовой пояс, и все привычки будут считать дни именно по твоему времени 🌍"
    )
    await message.answer(text, reply_markup=main_menu_kb())

# -------------------------------
# 🔹 Обработка кнопок меню
# -------------------------------
@router.message(lambda m: m.text in {"🏆 Рейтинг", "👤 Профиль"})
async def process_reply_buttons(message: types.Message):
    text = message.text

    # ---- 🏆 РЕЙТИНГ ----
    if text == "🏆 Рейтинг":
        await message.answer("🏆 Рейтинг: скоро будет.")

    # ---- 👤 ПРОФИЛЬ ----
    elif text == "👤 Профиль":
        await message.answer("👤 Твой профиль: в разработке.")

