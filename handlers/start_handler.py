import pytz
import logging
from aiogram import F
from datetime import datetime
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database import get_pool
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from repositories.affiliate_repository import (
    get_affiliate_by_code,
    create_referral,
    user_already_has_affiliate,
    user_exists_in_users_table,
)

# -------------------------------
# 🔹 LOGGING
# -------------------------------
logging.basicConfig(level=logging.INFO)


router = Router()


class NicknameFSM(StatesGroup):
    waiting_for_nickname = State()


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Активные задания")],
            [KeyboardButton(text="🏆 Рейтинг"), KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="➕ Добавить привычку / челлендж")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие…",
    )


def extract_referral_code(message: types.Message) -> str | None:
    if not message.text:
        return None

    parts = message.text.split()
    if len(parts) < 2:
        return None

    ref = parts[1].strip() or None
    logging.info(f"📎 Из сообщения извлечён реферальный код: {ref}")
    return ref


@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    logging.info(f"🚀 /start от user_id={message.from_user.id}")

    user_timezone = "Europe/Kyiv"
    if message.from_user and message.from_user.language_code == "en":
        user_timezone = "Europe/London"
    elif message.from_user and message.from_user.language_code == "uk":
        user_timezone = "Europe/Kyiv"
    elif message.from_user and message.from_user.language_code == "ru":
        user_timezone = "Europe/Moscow"

    logging.info(f"🌍 Язык пользователя: {message.from_user.language_code}, timezone={user_timezone}")

    ref_code = extract_referral_code(message)
    user_id = message.from_user.id

    existed_before = await user_exists_in_users_table(user_id)
    logging.info(f"👤 existed_before={existed_before}")

    pool = await get_pool()
    async with pool.acquire() as conn:
        logging.info("💾 Открыто соединение с БД")

        await conn.execute(
            """
            INSERT INTO users (user_id, username, first_name, timezone)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) DO UPDATE
              SET username = EXCLUDED.username,
                  first_name = EXCLUDED.first_name,
                  timezone = EXCLUDED.timezone
            """,
            user_id,
            message.from_user.username,
            message.from_user.first_name,
            user_timezone,
        )
        logging.info(f"💾 Пользователь сохранён/обновлён в БД: {user_id}")

        if ref_code:
            logging.info(f"🔍 Проверяем аффилиейт-код: {ref_code}")
            affiliate_id = await get_affiliate_by_code(ref_code)

            logging.info(f"👥 affiliate_id={affiliate_id}")

            if affiliate_id and affiliate_id != user_id:
                if existed_before:
                    logging.info("⛔ Пользователь не новый — рефералка НЕ присваивается")
                    pass
                else:
                    already = await user_already_has_affiliate(user_id)
                    logging.info(f"🔍 Проверка: есть ли уже реферал? {already}")

                    if not already:
                        await create_referral(
                            affiliate_id=affiliate_id,
                            user_id=user_id
                        )
                        logging.info(f"🎊 Реферал создан: {affiliate_id} ← {user_id}")

                        try:
                            await message.bot.send_message(
                                affiliate_id,
                                f"🎉 У тебя новый реферал: @{message.from_user.username or user_id}"
                            )
                            logging.info(f"📨 Уведомление рефереру отправлено: {affiliate_id}")
                        except Exception as e:
                            logging.error(f"❗ Ошибка отправки уведомления рефереру: {e}")

        nickname = await conn.fetchval(
            "SELECT nickname FROM users WHERE user_id = $1", user_id
        )
        logging.info(f"🔎 Nickname найден: {nickname}")

    if not nickname:
        logging.info("📝 Никнейма нет — просим пользователя ввести")
        await message.answer(
            "Привет! ✌️ Перед тем как начать, введи свой никнейм (имя, под которым тебя будут видеть другие):",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(NicknameFSM.waiting_for_nickname)
        logging.info("⏳ FSM: waiting_for_nickname")
        return

    logging.info("📲 Ник существует — показываем меню пользователю")
    await message.answer(
        "<b>Привет! ✌️ Я — Your Ambitions бот.</b>\n\n"
        "<b>Первый в своем роде трекер привычек онлайн. Ты видишь всех - все видят тебя. Развиваемся вместе!</b>\n\n"
        "<b>Я могу быть кем тебе удобно:</b>\n"
        "🤝 <b>другом</b>, который поддержит и не осудит,\n"
        "🎮 <b>игрой</b>, в которой ты прокачиваешь себя,\n"
        "⚔️ <b>спартанцем</b>, который заставит не сдаваться,\n"
        "🧠 <b>наставником</b>, который помогает расти,\n"
        "📓 или даже <b>личной зачёткой</b>, где записаны твои победы.\n\n"
        "<b>Я буду напоминать о привычках, вести твой прогресс и помогать держать дисциплину каждый день.</b>\n"
        "Давай топить вместе, братуха. Ты не один — я рядом. 💪🔥\n\n"
        "<b>Начни с добавления привычки или челленджа.</b>\n"
        "Настроить мой стиль поведения и тон уведомлений можешь в «Профиль → Настройки».",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


@router.message(NicknameFSM.waiting_for_nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    logging.info(f"🆕 Пользователь вводит ник: '{message.text}'")

    nickname = message.text.strip()

    if nickname.startswith("@"):
        nickname = nickname[1:]

    if not nickname:
        logging.info("❗ Пустой никнейм")
        await message.answer("❗️Никнейм не может быть пустым. Попробуй снова:")
        return
    if len(nickname) > 20:
        logging.info("❗ Никнейм слишком длинный")
        await message.answer("❗️Никнейм слишком длинный. Введи короче (до 20 символов):")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        existing_user = await conn.fetchval(
            "SELECT user_id FROM users WHERE LOWER(nickname) = LOWER($1)",
            nickname
        )
        logging.info(f"🔎 Проверяем занятость ника: {nickname} → exists={existing_user}")

        if existing_user and existing_user != message.from_user.id:
            logging.info("⛔ Ник занят другим пользователем")
            await message.answer(
                f"❗️Ник '{nickname}' уже используется другим пользователем.\n"
                f"Попробуй другой вариант:"
            )
            return

        await conn.execute(
            "UPDATE users SET nickname = $1 WHERE user_id = $2",
            nickname,
            message.from_user.id
        )
        logging.info(f"💾 Ник сохранён: {message.from_user.id} → {nickname}")

    logging.info("🎉 Ник успешно установлен, показываем меню")
    await message.answer(
        f"<b>Отлично, {nickname}! ✌️ Я — Your Ambitions бот.</b>\n\n"
        "<b>Я могу быть кем тебе удобно:</b>\n"
        "🤝 <b>другом</b>, который поддержит и не осудит,\n"
        "🎮 <b>игрой</b>, в которой ты прокачиваешь себя,\n"
        "⚔️ <b>спартанцем</b>, который заставит не сдаваться,\n"
        "🧠 <b>наставником</b>, который помогает расти,\n"
        "📓 или даже <b>личной зачёткой</b>, где записаны твои победы.\n\n"
        "<b>Я буду напоминать о привычках, вести твой прогресс и помогать держать дисциплину каждый день.</b>\n"
        "Давай топить вместе, братуха. Ты не один — я рядом. 💪🔥\n\n"
        "<b>Начни с добавления привычки или челленджа.</b>\n"
        "Настроить мой стиль поведения и тон уведомлений можешь в «Профиль → Настройки».",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )
    logging.info("🧼 FSM cleared")
    await state.clear()
