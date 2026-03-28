import pytz
import logging
from aiogram import F
from html import escape
from datetime import datetime
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.database import get_pool
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from repositories.affiliate_repository import (
    get_affiliate_by_code,
    create_referral,
    user_already_has_affiliate,
    user_exists_in_users_table,
    generate_referral_code,  
    assign_referral_code 
)

from services.achievements.achievements_service import process_achievements_and_notify





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
       #     [KeyboardButton(text="🏆 Рейтинг"), KeyboardButton(text="👤 Профиль")],
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
    logging.info(f"🚀 /start от user_id={message.from_user.id} (chat_type={message.chat.type})")

    # 🔥 Блокируем /start в группах и каналах
    if message.chat.type != "private":
        logging.warning(
            f"⛔ /start заблокирован! user_id={message.from_user.id}, "
            f"username=@{message.from_user.username}, chat_id={message.chat.id}, "
            f"chat_type={message.chat.type}"
        )
        await message.answer("⚠️ Команду /start можно использовать только в личном чате с ботом.")
        return

    # Определяем timezone
    user_timezone = "Europe/Kyiv"

    ref_code = extract_referral_code(message)
    user_id = message.from_user.id

    # Есть ли этот пользователь в БД?
    existed_before = await user_exists_in_users_table(user_id)
    logging.info(f"👤 existed_before={existed_before}")

    # -----------------------------
    # 1. СОЗДАЕМ ПОЛЬЗОВАТЕЛЯ
    # -----------------------------
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
                  timezone = COALESCE(users.timezone, EXCLUDED.timezone)
            """,
            user_id,
            message.from_user.username,
            message.from_user.first_name,
            user_timezone,
        )

        # 🔹 создаём запись статистики (если нет)
        await conn.execute("""
            INSERT INTO user_stats (user_id)
            VALUES ($1)
            ON CONFLICT (user_id) DO NOTHING
        """, user_id)

    logging.info(f"💾 Пользователь сохранён/обновлён в БД: {user_id}")

    # -----------------------------
    # 2. ОБРАБОТКА РЕФЕРАЛКИ (ПОСЛЕ СОЗДАНИЯ!)
    # -----------------------------
    if ref_code and not existed_before:
        logging.info(f"🔍 Проверяем аффилиейт-код: {ref_code}")
        affiliate_id = await get_affiliate_by_code(ref_code)
        logging.info(f"👥 affiliate_id={affiliate_id}")

        if affiliate_id and affiliate_id != user_id:
            already = await user_already_has_affiliate(user_id)

            if not already:
                await create_referral(affiliate_id, user_id)
                logging.info(f"🎊 Реферал создан: {affiliate_id} ← {user_id}")

                # 📩 Сначала уведомляем партнёра
                try:
                    await message.bot.send_message(
                        affiliate_id,
                        f"🎉 У тебя новый реферал: @{message.from_user.username or user_id}"
                    )
                except Exception as e:
                    logging.error(
                        f"❗ Ошибка отправки уведомления рефереру: {e}"
                    )

                # 🏆 Затем проверяем и выдаём достижения
                pool = await get_pool()
                async with pool.acquire() as conn:
                    await process_achievements_and_notify(
                        message.bot,
                        conn,
                        affiliate_id,
                        trigger_types=["referrals_count"]
                    )

    # -----------------------------
    # 3. ГЕНЕРАЦИЯ РЕФЕРАЛЬНОГО КОДА
    # -----------------------------
    pool = await get_pool()
    async with pool.acquire() as conn:
        current_code = await conn.fetchval(
            "SELECT referral_code FROM users WHERE user_id = $1",
            user_id
        )

        if not current_code:
            new_code = await generate_referral_code(user_id)
            await assign_referral_code(user_id, new_code)
            logging.info(f"🎯 Пользователю {user_id} присвоен рефкод: {new_code}")

        nickname = await conn.fetchval(
            "SELECT nickname FROM users WHERE user_id = $1",
            user_id
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

    await message.answer(
        welcome_text(nickname) + "<b>Добавь первую привычку или выбери челлендж:👇</b>",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )



@router.message(NicknameFSM.waiting_for_nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    logging.info(f"🆕 Пользователь вводит ник: '{message.text}'")

    nickname = message.text.strip()

    if nickname.startswith("@"):
        nickname = nickname[1:]

    # 🔐 Защита от HTML (<b>boss</b> и т.п.)
    nickname = escape(nickname)

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
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Добавить привычку / челлендж",
                callback_data="open_add_menu"
            )]
        ]
    )
 
    await message.answer(
        welcome_text(nickname) + "<b>Добавь первую привычку или выбери челлендж:👇</b>",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


    logging.info("🧼 FSM cleared")
    await state.clear()


def welcome_text(nickname: str | None = None) -> str:
    name = f"{nickname}, " if nickname else ""
    return (
        f"<b>Добро пожаловать в систему, {name}</b>\n\n"
        "Здесь ты не просто ставишь цели —\n"
        "ты показываешь, на что реально способен.\n\n"
        "<b>📌 Бот делится на 2 части:</b>\n\n"
        "<b>1️⃣ ДЕЙСТВИЕ</b>\n"
        "— добавляешь привычки\n"
        "— берёшь челленджи\n"
        "— подтверждаешь выполнение\n\n"
        "Все подтверждения попадают в общий чат:\n"
        "👉 <a href=\"https://t.me/yourambitions_chat\">перейти в чат</a>\n\n"
        "Здесь нет скрытой работы.\n"
        "<b>Либо сделал — либо нет.</b>\n\n"
        "<b>2️⃣ АНАЛИТИКА</b>\n"
        "— твой прогресс\n"
        "— уровень дисциплины\n"
        "— сравнение с другими\n\n"
        "Ты видишь правду о себе.\n"
        "<b>Без иллюзий.</b>\n\n"
        "⚠️ <b>Важно:</b>\n"
        "Не добавляй сразу всё.\n"
        "Начни с 1–2 привычек и доведи их до результата.\n\n"
    )
