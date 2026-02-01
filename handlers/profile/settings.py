#handlers/profile/settings
from aiogram import Router, F, types
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest

from handlers.profile.settings_timezone import (
    timezone_keyboard,
    get_timezone_display
)

import logging

from config import PUBLIC_CHAT_ID, CHAT_USERNAME
from services.profile_settings_service import profile_settings_service

router = Router()
logger = logging.getLogger(__name__)


# =====================================================
# 🔹 Проверка: состоит ли пользователь в чате
# =====================================================
async def is_user_in_public_chat(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(PUBLIC_CHAT_ID, user_id)
        return member.status not in ("left", "kicked")
    except TelegramBadRequest:
        return False


# =====================================================
# ⚙️ Настройки профиля
# =====================================================
@router.callback_query(F.data == "profile_settings")
async def show_profile_settings(callback: CallbackQuery):
    user_id = callback.from_user.id
    bot = callback.bot

    logger.info(f"[SETTINGS] Пользователь {user_id} открыл настройки профиля")

    settings = await profile_settings_service.get_settings_for_user(user_id)

    # --- Проверяем участие в чате ---
    in_chat = await is_user_in_public_chat(bot, user_id)

    tz = settings.get("timezone")
    timezone_label = get_timezone_display(tz)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Друг 🤝", callback_data="tone_friend"),
            InlineKeyboardButton(text="Игровой 🎮", callback_data="tone_gamer"),
            InlineKeyboardButton(text="Спартанец ⚔️", callback_data="tone_spartan"),
        ],
        timezone_keyboard(tz).inline_keyboard[0],
        [
            InlineKeyboardButton(
                text=f"Публикация медиа: {'🟢 Вкл' if settings['share_on'] else '⚪ Выкл'}",
                callback_data="toggle_share_media"
            )
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile_menu")
        ]
    ])

    if not in_chat:
        keyboard.inline_keyboard.insert(
            -1,
            [
                InlineKeyboardButton(
                    text="💬 Вступить в общий чат",
                    url=f"https://t.me/{CHAT_USERNAME}"
                )
            ]
        )

    text = (
        f"⚙️ <b>Настройки</b>\n\n"
        f"🔔 Тон уведомлений: <b>{settings['tone_label']}</b>\n"
        f"🕒 Регион: <b>{timezone_label}</b>\n"
        f"📢 Публикация медиа: <b>{'🟢 Вкл' if settings['share_on'] else '⚪ Выкл'}</b>\n\n"
        f"Выбери нужные параметры 👇"
    )

    try:
        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logger.info("[SETTINGS] Сообщение не изменилось")
        else:
            logger.error(f"[SETTINGS] Ошибка Telegram: {e}")
            raise

    await callback.answer()



# =====================================================
# 🧘 Изменение тона уведомлений
# =====================================================
@router.callback_query(F.data.startswith("tone_"))
async def set_notification_tone(callback: CallbackQuery):
    user_id = callback.from_user.id
    tone_code = callback.data.replace("tone_", "")

    logger.info(f"[SETTINGS] Пользователь {user_id} выбрал тон: {tone_code}")

    ok = await profile_settings_service.set_tone(user_id, tone_code)
    if not ok:
        logger.warning(f"[SETTINGS] Некорректный тон от пользователя {user_id}")
        await callback.answer("❌ Неверный выбор", show_alert=True)
        return

    await callback.answer("✅ Стиль уведомлений обновлён")
    await show_profile_settings(callback)


# =====================================================
# 🔄 Переключение публикации медиа
# =====================================================
@router.callback_query(F.data == "toggle_share_media")
async def toggle_share_media(callback: CallbackQuery):
    user_id = callback.from_user.id

    logger.info(f"[SETTINGS] Пользователь {user_id} переключил публикацию медиа")

    await profile_settings_service.toggle_share_media_option(user_id)

    await callback.answer("👌 Обновлено")
    await show_profile_settings(callback)
