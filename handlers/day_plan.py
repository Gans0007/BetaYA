from aiogram import Router, types
from datetime import datetime
from zoneinfo import ZoneInfo

from core.database import get_pool

router = Router()


@router.message(lambda m: m.text == "📋 План на завтра")
async def show_day_plan(message: types.Message):
    user_id = message.from_user.id

    # 🔹 Получаем timezone пользователя
    pool = await get_pool()
    async with pool.acquire() as conn:
        tz_name = await conn.fetchval(
            "SELECT timezone FROM users WHERE user_id=$1",
            user_id
        )

    tz_name = tz_name or "Europe/Kyiv"

    try:
        now = datetime.now(ZoneInfo(tz_name))
    except Exception as e:
        print("Timezone error:", e)
        now = datetime.now(ZoneInfo("Europe/Kyiv"))

    hour = now.hour

    # ================================
    # 🌙 ВЕЧЕР — МОЖНО ПЛАНИРОВАТЬ
    # ================================
    if 20 <= hour < 23:
        await message.answer(
            "📋 <b>План на завтра</b>\n\n"
            "Завтрашний день начинается сегодня.\n"
            "Добавь задачи, которые обязательно нужно выполнить.\n\n"
            "⏰ Планирование открыто с 20:00 до 23:00",
            parse_mode="HTML"
        )
        return

    # ================================
    # ⛔ В ДРУГОЕ ВРЕМЯ — ЗАКРЫТО
    # ================================
    await message.answer(
        "⛔ <b>Планирование закрыто</b>\n\n"
        "План составляется вечером.\n"
        "Сильные люди готовят день заранее.\n\n"
        "Возвращайся с 20:00 до 23:00",
        parse_mode="HTML"
    )