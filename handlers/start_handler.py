import pytz
from datetime import datetime
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database import get_pool
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

# -------------------------------
# 🔹 FSM для ввода никнейма
# -------------------------------
class NicknameFSM(StatesGroup):
    waiting_for_nickname = State()


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
async def start_command(message: types.Message, state: FSMContext):
    user_timezone = "Europe/Kyiv"
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

        nickname = await conn.fetchval(
            "SELECT nickname FROM users WHERE user_id = $1", message.from_user.id
        )

    # Если никнейма нет — просим ввести и убираем все кнопки
    if not nickname:
        await message.answer(
            "Привет! ✌️ Перед тем как начать, введи свой никнейм (имя, под которым тебя будут видеть другие):",
            reply_markup=ReplyKeyboardRemove(),  # ❌ убираем все кнопки
        )
        await state.set_state(NicknameFSM.waiting_for_nickname)
        return

    # Если ник уже есть — показываем меню
    await message.answer(
        "Привет! ✌️ Я — Your Ambitions бот.\n\n"
        "Я могу быть кем тебе удобно:\n"
        "🤝 другом, который поддержит и не осудит,\n"
        "🎮 игрой, в которой ты прокачиваешь себя,\n"
        "⚔️ спартанцем, который заставит не сдаваться,\n"
        "🧠 наставником, который помогает расти,\n"
        "📓 или даже личной зачёткой, где записаны твои победыв.\n\n"
        "Я буду напоминать о привычках, вести твой прогресс и помогать держать дисциплину каждый день.\n"
        "Давай топить вместе, братуха. Ты не один — я рядом. 💪🔥\n\n"
        "Настроить мой стиль поведения и тон уведомлений можешь в «Профиль → Настройки».",
        reply_markup=main_menu_kb()
    )


# -------------------------------
# 🔹 Обработка никнейма
# -------------------------------
@router.message(NicknameFSM.waiting_for_nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    nickname = message.text.strip()

    # Убираем @ если пользователь ввёл его
    if nickname.startswith("@"):
        nickname = nickname[1:]

    # Проверяем длину и пустоту
    if not nickname:
        await message.answer("❗️Никнейм не может быть пустым. Попробуй снова:")
        return
    if len(nickname) > 20:
        await message.answer("❗️Никнейм слишком длинный. Введи короче (до 20 символов):")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        # Проверяем, занят ли ник
        existing_user = await conn.fetchval(
            "SELECT user_id FROM users WHERE LOWER(nickname) = LOWER($1)",
            nickname
        )
        if existing_user and existing_user != message.from_user.id:
            await message.answer(
                f"❗️Ник '{nickname}' уже используется другим пользователем.\n"
                f"Попробуй другой вариант:"
            )
            return

        # Если ник свободен — сохраняем
        await conn.execute(
            "UPDATE users SET nickname = $1 WHERE user_id = $2",
            nickname,
            message.from_user.id
        )

    await message.answer(
        f"Отлично, {nickname}! ✅\nТеперь можешь пользоваться ботом.",
        reply_markup=main_menu_kb()
    )
    await state.clear()
