from datetime import datetime
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging
import pytz


from core.database import get_pool

router = Router()
logger = logging.getLogger(__name__)

# =====================================================
# 🌍 Регионы и таймзоны (ЕДИНЫЙ ИСТОЧНИК ПРАВДЫ)
# =====================================================
TIMEZONE_REGIONS = {
    "ua": ("🇺🇦", "Kyiv", "Europe/Kyiv"),
    "ru": ("🇷🇺", "Moscow", "Europe/Moscow"),
    "pl": ("🇵🇱", "Warsaw", "Europe/Warsaw"),
    "de": ("🇩🇪", "Berlin", "Europe/Berlin"),
    "us": ("🇺🇸", "Vancouver", "America/Vancouver"),
}


# =====================================================
# 🏷️ ДИСПЛЕЙ В ФОРМАТЕ ФЛАГ РЕГИОН ВРЕМЯ
# =====================================================
def get_timezone_display(tz: str | None) -> str:
    if not tz:
        return "—"

    for flag, city, timezone in TIMEZONE_REGIONS.values():
        if timezone == tz:
            now = datetime.now(pytz.timezone(timezone))
            time_str = now.strftime("%H:%M")
            return f"{flag} {city} {time_str}"

    return "—"


# =====================================================
# ⌨️ Inline-клавиатура (1 ряд, 5 флагов)
# =====================================================
def timezone_keyboard(selected_tz: str | None = None) -> InlineKeyboardMarkup:
    buttons = []

    for code, (flag, city, timezone) in TIMEZONE_REGIONS.items():
        buttons.append(
            InlineKeyboardButton(
                text=flag,
                callback_data=f"tz:{code}"
            )
        )

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


# =====================================================
# ✅ Выбор региона (callback tz:*)
# =====================================================
@router.callback_query(F.data.startswith("tz:"))
async def set_timezone(callback: CallbackQuery):
    user_id = callback.from_user.id
    region_code = callback.data.split(":", 1)[1]

    if region_code not in TIMEZONE_REGIONS:
        await callback.answer("❌ Неверный регион", show_alert=True)
        return

    flag, city, timezone = TIMEZONE_REGIONS[region_code]  # ✅ ВАЖНО

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET timezone = $1 WHERE user_id = $2",
            timezone,
            user_id
        )

    logger.info(
        f"[TIMEZONE] Пользователь {user_id} установил таймзону {timezone}"
    )

    from handlers.profile.settings import show_profile_settings

    await callback.answer("🕒 Регион обновлён")
    await show_profile_settings(callback)

    # 🔁 ПЕРЕРИСОВКА КАРТОЧКИ
    from handlers.profile.settings import show_profile_settings

    await callback.answer("🕒 Регион обновлён")
    await show_profile_settings(callback)




