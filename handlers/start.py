import logging
from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from utils.check_subs import check_subscription
from keyboards.menu import get_main_menu
from aiogram.exceptions import TelegramBadRequest
import config
import random
from aiogram.fsm.context import FSMContext
from handlers.rules_text import JOIN_MESSAGES

from repositories.profiles.profile_repository import save_user, get_user
from repositories.referrals.referral_repo import save_referral

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def start_cmd(message: types.Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"[START] Пользователь {user_id} начал работу")

    user = await get_user(user_id)

    # Попробуем достать реферальный ID, если он передан
    referrer_id = None
    if user is None and message.text and len(parts := message.text.split()) == 2 and parts[1].isdigit():
        referrer_id = int(parts[1])
        logger.info(f"[REFERRAL] Новый пользователь {user_id} перешёл по ссылке от {referrer_id}")
        await state.update_data(referrer_id=referrer_id)
    else:
        logger.info(f"[REFERRAL] Пользователь {user_id} уже зарегистрирован — пропускаем сохранение реферала")

    # ⚠️ Уведомление и сохранение связи теперь происходит в handle_check_subscription()

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(
            text="📢 Подписаться на канал", url=f"https://t.me/{config.CHANNEL_USERNAME.strip('@')}"
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text="💬 Подписаться на чат", url=f"https://t.me/{config.CHAT_USERNAME.strip('@')}"
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text="✅ Проверить подписку", callback_data="check_subs"
        )
    )

    try:
        photo = "AgACAgIAAxkBAAKWXmiDtgABwqjNHrPJ0M7hHk6W6aFEhgACgfcxG5VxGUifYHenfAVR1gEAAwIAA3gAAzYE"
        await message.answer_photo(
            photo=photo,
            caption=(
                "Привет!\n"
                "Этот бот помогает собраться, прокачать дисциплину и довести дела до конца.\n\n"
                "Каждый день ты будешь отмечать простые шаги и видеть, "
                "как они превращаются в результат.\n\n"
                "Хочешь попробовать начать сегодня?\n\n"
                "Чтобы пользоваться ботом — подпишись на канал и чат ниже 👇"
            ),
            reply_markup=keyboard.as_markup()
        )

    except Exception as e:
        logger.critical(f"[START] Не удалось отправить стартовое фото пользователю {user_id}: {e}")
        await message.answer("❌ Не удалось отправить стартовое сообщение. Попробуй позже.")


@router.callback_query(lambda c: c.data == "check_subs")
async def handle_check_subscription(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id
    logger.info(f"[SUB_CHECK] Проверка подписки для пользователя {user_id}")

    # ⚡ СРАЗУ отвечаем на callback, чтобы Telegram не вырубил
    try:
        await callback.answer("⏳ Проверяю подписку...", show_alert=False)
    except Exception as e:
        logger.warning(f"[CALLBACK] Не удалось ответить Telegram вовремя для пользователя {user_id}: {e}")

    try:
        sub_channel = await check_subscription(bot, user_id, config.CHANNEL_USERNAME)
        sub_chat = await check_subscription(bot, user_id, config.CHAT_USERNAME)
    except Exception as e:
        logger.error(f"[ERROR] Ошибка при проверке подписки пользователя {user_id}: {e}")
        await callback.message.answer("❌ Ошибка при проверке подписки. Попробуй позже.")
        return

    if sub_channel and sub_chat:
        logger.info(f"[SUB_CHECK] Подписка подтверждена для пользователя {user_id}")

        full_name = callback.from_user.full_name or "-"
        try:
            await save_user(user_id, full_name)
            logger.info(f"[DB] Пользователь {user_id} сохранён в базе")

            # 👥 Попробуем достать referrer_id из FSM
            data = await state.get_data()
            referrer_id = data.get("referrer_id")

            if referrer_id:
                try:
                    await save_referral(referrer_id, user_id, bot)
                    logger.info(f"[REFERRAL] ✅ Сохранена связь: {referrer_id} → {user_id}")

                    # ✅ Уведомление пригласившему
                    try:
                        inviter_msg = random.choice(JOIN_MESSAGES).format(name=callback.from_user.full_name)
                        await bot.send_message(referrer_id, inviter_msg, parse_mode="HTML")
                        logger.info(f"[REFERRAL] ✅ Уведомление отправлено пригласившему {referrer_id}")
                    except TelegramBadRequest as e:
                        logger.warning(f"[REFERRAL] ⚠️ Не удалось отправить уведомление {referrer_id}: {e}")

                except Exception as e:
                    logger.error(f"[REFERRAL] ❌ Ошибка при сохранении связи {referrer_id} → {user_id}: {e}")

        except Exception as e:
            logger.error(f"[DB] Ошибка сохранения пользователя {user_id}: {e}") 

        await callback.message.answer(
            text=(
                "🧭 <b>Краткая инструкция</b>:\n\n"
                "📌 <b>Добавить привычку Challenge</b> — создай новую привычку и начни прокачку.\n\n"
                "📌 <b>Активное задание</b> — здесь хранятся все твои активные привычки.\n\n"
                "📌 <b>Подтверждение привычки</b> — через кнопку «Подтвердить» в активных заданиях.\n"
                "Можно также отправить видео или кружочек прямо в чат с ботом и выбрать нужную привычку.\n\n"
                "После подтверждения видео попадёт в общий чат с прогрессом.\n\n"
                "Удачи, друг! 💪"
            ),
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        return

    logger.info(f"[SUB_CHECK] Пользователь {user_id} ещё не подписан (канал: {sub_channel}, чат: {sub_chat})")

    text = "❌ Брат, ты ещё не подписан:\n"
    if not sub_channel:
        text += f"📢 <a href='https://t.me/{config.CHANNEL_USERNAME.strip('@')}'>Подпишись на канал</a>\n"
    if not sub_chat:
        text += f"💬 <a href='https://t.me/{config.CHAT_USERNAME.strip('@')}'>Подпишись на чат</a>\n"

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(
            text="📢 Подписаться на канал", url=f"https://t.me/{config.CHANNEL_USERNAME.strip('@')}")
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text="💬 Подписаться на чат", url=f"https://t.me/{config.CHAT_USERNAME.strip('@')}")
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text="✅ Проверить подписку", callback_data="check_subs")
    )

    await callback.message.answer(text, reply_markup=keyboard.as_markup(), parse_mode="HTML")


    await callback.message.answer(text, reply_markup=keyboard.as_markup(), parse_mode="HTML")
    await callback.answer("Проверь подписку и попробуй снова.", show_alert=True)
