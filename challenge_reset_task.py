import asyncio
from datetime import datetime
import pytz
from database import get_pool

async def check_challenge_resets():
    """
    Ежедневная проверка пропусков челленджей.
    Логика основана на difficulty (1–3).
    """
    while True:
        pool = await get_pool()
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)

        async with pool.acquire() as conn:
            active = await conn.fetch("""
                SELECT h.id, h.user_id, h.challenge_id, h.name,
                       h.done_days, h.days, h.difficulty,
                       u.timezone
                FROM habits h
                JOIN users u ON u.user_id = h.user_id
                WHERE h.is_challenge = TRUE AND h.is_active = TRUE
            """)

        for ch in active:
            user_tz = pytz.timezone(ch["timezone"] or "Europe/Kyiv")
            local_now = now_utc.astimezone(user_tz)

            # последнее подтверждение
            async with pool.acquire() as conn:
                last_confirm = await conn.fetchval("""
                    SELECT datetime FROM confirmations
                    WHERE user_id=$1 AND habit_id=$2
                    ORDER BY datetime DESC LIMIT 1
                """, ch["user_id"], ch["id"])

            if not last_confirm:
                continue

            last_local = last_confirm.astimezone(user_tz)
            days_missed = (local_now.date() - last_local.date()).days

            difficulty = ch["difficulty"]

            # ⭐ Легко — без сброса
            if difficulty == 1:
                continue

            # ⭐⭐ Средне — сброс после 2 пропусков подряд
            if difficulty == 2 and days_missed >= 2:
                await reset_challenge(pool, ch, "2 дня подряд без подтверждения")
                continue

            # ⭐⭐⭐ Сложно — сброс после 1 пропуска
            if difficulty == 3 and days_missed >= 1:
                await reset_challenge(pool, ch, "1 день пропуска")

        await asyncio.sleep(24 * 60 * 60)

async def reset_challenge(pool, ch, reason):
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM habits WHERE id=$1", ch["id"])

    from aiogram import Bot
    from config import BOT_TOKEN

    bot = Bot(BOT_TOKEN)
    try:
        await bot.send_message(
            ch["user_id"],
            f"⚠️ Челлендж *{ch['name']}* сброшен!\nПричина: {reason}",
            parse_mode="Markdown"
        )
    finally:
        await bot.session.close()
