from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest
import logging

from services.profile_settings_service import profile_settings_service

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


@router.callback_query(F.data == "profile_settings")
async def show_about_options(callback: CallbackQuery):
    user_id = callback.from_user.id

    logging.info(f"[OPTIONS] Пользователь {user_id} открыл меню настроек профиля")

    settings = await profile_settings_service.get_settings_for_user(user_id)

    logging.info(f"[OPTIONS] Настройки пользователя {user_id}: тон = {settings['tone_label']}, share_on = {settings['share_on']}")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Друг🤝", callback_data="tone_friend"),
            InlineKeyboardButton(text="Игровой🎮", callback_data="tone_gamer"),
            InlineKeyboardButton(text="Спартанец⚔️", callback_data="tone_spartan"),
        ],
        [
            InlineKeyboardButton(
                text=f"Публикация медиа в общий чат: {'🟢 Вкл' if settings['share_on'] else '⚪ Выкл'}",
                callback_data="toggle_share_media"
            )
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile_menu")]
    ])

    text = (
        f"⚙️ <b>Настройки</b>\n\n"
        f"🔔 Тон уведомлений: <b>{settings['tone_label']}</b>\n"
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
            logging.info(f"[OPTIONS] Сообщение не изменилось — Telegram не обновил текст")
            pass
        else:
            logging.error(f"[OPTIONS] Ошибка Telegram: {e}")
            raise

    await callback.answer()


# 🧘 Изменение тона уведомлений
@router.callback_query(F.data.startswith("tone_"))
async def set_notification_tone(callback: CallbackQuery):
    user_id = callback.from_user.id
    tone_code = callback.data.replace("tone_", "")

    logging.info(f"[OPTIONS] Пользователь {user_id} выбрал тон уведомлений: {tone_code}")

    ok = await profile_settings_service.set_tone(user_id, tone_code)
    if not ok:
        logging.warning(f"[OPTIONS] Некорректный тон уведомлений от пользователя {user_id}: {tone_code}")
        await callback.answer("❌ Неверный выбор", show_alert=True)
        return

    logging.info(f"[OPTIONS] Тон уведомлений успешно обновлен для пользователя {user_id}")

    await callback.answer("✅ Стиль уведомлений обновлён")
    await show_about_options(callback)


# 🔄 Переключение публикации медиа
@router.callback_query(F.data == "toggle_share_media")
async def toggle_share_media(callback: CallbackQuery):
    user_id = callback.from_user.id

    logging.info(f"[OPTIONS] Пользователь {user_id} переключил параметр публикации медиа")

    result = await profile_settings_service.toggle_share_media_option(user_id)

    logging.info(f"[OPTIONS] Статус share_on теперь: {result}")

    await callback.answer("👌 Обновлено")
    await show_about_options(callback)
