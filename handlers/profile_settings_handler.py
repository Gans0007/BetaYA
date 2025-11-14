# ---------- НАСТРОЙКИ (РУССКАЯ ВЕРСИЯ С ВЫБОРОМ ЯЗЫКА) ----------

from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from database import get_pool

router = Router()

# -------------------------------
# Варианты уведомлений и языков
# -------------------------------
NOTIFICATION_TONES = {
    "friend": "Друг🤝",
    "gamer": "Игровой🎮",
    "spartan": "Спартанец⚔️",
}

LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "uk": "🇺🇦 Українська",
    "en": "🇬🇧 English",
}


# -------------------------------
# Главное меню настроек
# -------------------------------
@router.callback_query(F.data == "profile_settings")
async def show_about_options(callback: CallbackQuery):
    """Показывает меню настроек (русская версия с выбором языка)"""
    user_id = callback.from_user.id
    pool = await get_pool()

    async with pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT notification_tone, share_confirmation_media, language
            FROM users
            WHERE user_id = $1
        """, user_id)

    tone_code = user["notification_tone"] if user and user["notification_tone"] else "mixed"
    share_on = user["share_confirmation_media"] if user and user["share_confirmation_media"] is not None else True
    lang_code = user["language"] if user and user["language"] else "ru"

    tone_label = NOTIFICATION_TONES.get(tone_code, "Друг🤝")
    share_label = "🟢 Вкл" if share_on else "⚪ Выкл"
    lang_label = LANGUAGES.get(lang_code, "🇷🇺 Русский")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Друг🤝", callback_data="tone_friend"),
            InlineKeyboardButton(text="Игровой🎮", callback_data="tone_gamer"),
            InlineKeyboardButton(text="Спартанец⚔️", callback_data="tone_spartan"),
        ],
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ],
        [
            InlineKeyboardButton(
                text=f"Публикация медиа в общий чат: {share_label}",
                callback_data="toggle_share_media"
            )
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile_menu")]
    ])

    await callback.message.edit_text(
        text=(
            f"⚙️ <b>Настройки</b>\n\n"
            f"🔔 Тон уведомлений: <b>{tone_label}</b>\n"
            f"🌐 Язык интерфейса: <b>{lang_label}</b>\n"
            f"📢 Публикация медиа: <b>{share_label}</b>\n\n"
            f"Выбери нужные параметры 👇"
        ),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


# -------------------------------
# 🧘 Изменение стиля уведомлений
# -------------------------------
@router.callback_query(F.data.startswith("tone_"))
async def set_notification_tone(callback: CallbackQuery):
    """Изменение тона уведомлений"""
    user_id = callback.from_user.id

    tone_code = callback.data.replace("tone_", "")  # friend / gamer / spartan

    if tone_code not in NOTIFICATION_TONES:
        await callback.answer("❌ Неверный выбор", show_alert=True)
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET notification_tone = $1 WHERE user_id = $2",
            tone_code, user_id
        )

    await callback.answer("✅ Стиль уведомлений обновлён")
    await show_about_options(callback)



# -------------------------------
# 🌐 Смена языка интерфейса
# -------------------------------
@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    """Изменение языка интерфейса"""
    user_id = callback.from_user.id
    lang_code = callback.data.replace("lang_", "")

    if lang_code not in LANGUAGES:
        await callback.answer("❌ Неверный язык", show_alert=True)
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET language = $1 WHERE user_id = $2",
            lang_code, user_id
        )

    await callback.answer(f"✅ Язык интерфейса обновлён: {LANGUAGES[lang_code]}")
    await show_about_options(callback)


# -------------------------------
# 🔄 Переключение публикации медиа
# -------------------------------
@router.callback_query(F.data == "toggle_share_media")
async def toggle_share_media(callback: CallbackQuery):
    """Вкл/выкл публикацию медиа в общий чат"""
    user_id = callback.from_user.id
    pool = await get_pool()

    async with pool.acquire() as conn:
        current = await conn.fetchval(
            "SELECT share_confirmation_media FROM users WHERE user_id = $1",
            user_id
        )
        if current is None:
            current = True
        new_value = not current
        await conn.execute(
            "UPDATE users SET share_confirmation_media = $1 WHERE user_id = $2",
            new_value, user_id
        )

    await callback.answer("✅ Настройка обновлена")
    await show_about_options(callback)
