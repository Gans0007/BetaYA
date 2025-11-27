from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest  # 👈 добавь этот импорт

from services.profile_settings_service import profile_settings_service

router = Router()


@router.callback_query(F.data == "profile_settings")
async def show_about_options(callback: CallbackQuery):
    user_id = callback.from_user.id

    settings = await profile_settings_service.get_settings_for_user(user_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Друг🤝", callback_data="tone_friend"),
            InlineKeyboardButton(text="Игровой🎮", callback_data="tone_gamer"),
            InlineKeyboardButton(text="Спартанец⚔️", callback_data="tone_spartan"),
        ],
        [
            InlineKeyboardButton(text="Рус", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
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
        f"🌐 Язык интерфейса: <b>{settings['lang_label']}</b>\n"
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
        # Если пытаемся отправить то же самое сообщение с той же клавой — просто игнорим
        if "message is not modified" in str(e):
            pass
        else:
            raise

    await callback.answer()


# 🧘 Изменение тона уведомлений
@router.callback_query(F.data.startswith("tone_"))
async def set_notification_tone(callback: CallbackQuery):
    user_id = callback.from_user.id
    tone_code = callback.data.replace("tone_", "")

    ok = await profile_settings_service.set_tone(user_id, tone_code)
    if not ok:
        await callback.answer("❌ Неверный выбор", show_alert=True)
        return

    await callback.answer("✅ Стиль уведомлений обновлён")
    await show_about_options(callback)


# 🌐 Смена языка
@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang_code = callback.data.replace("lang_", "")

    ok = await profile_settings_service.set_language(user_id, lang_code)
    if not ok:
        await callback.answer("❌ Неверный язык", show_alert=True)
        return

    await callback.answer("👌 Язык обновлён")
    await show_about_options(callback)


# 🔄 Переключение публикации медиа
@router.callback_query(F.data == "toggle_share_media")
async def toggle_share_media(callback: CallbackQuery):
    user_id = callback.from_user.id

    result = await profile_settings_service.toggle_share_media_option(user_id)

    await callback.answer("👌 Обновлено")
    await show_about_options(callback)
