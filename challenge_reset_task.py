# challenge_reset_task.py
import asyncio
from datetime import datetime, timedelta
import pytz
from database import get_pool

async def check_challenge_resets():
    """
    Ежедневная проверка пропусков и аннулирование челленджей
    в зависимости от звезды (1–3).
    """
    while True:
        pool = await get_pool()
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)

        async with pool.acquire() as conn:
            # Берем все активные челленджи
            active_challenges = await conn.fetch("""
                SELECT h.id, h.user_id, h.challenge_id, h.name, h.done_days, h.days,
                       c.repeat_count, u.timezone
                FROM habits h
                JOIN completed_challenges c ON c.challenge_id = h.challenge_id
                JOIN users u ON u.user_id = h.user_id
                WHERE h.is_challenge = TRUE AND h.is_active = TRUE
            """)

        for ch in active_challenges:
            user_tz = pytz.timezone(ch["timezone"] or "Europe/Kyiv")
            user_now = now_utc.astimezone(user_tz)

            # ищем последнее подтверждение
            async with pool.acquire() as conn:
                last_confirm = await conn.fetchval("""
                    SELECT datetime FROM confirmations
                    WHERE user_id = $1 AND habit_id = $2
                    ORDER BY datetime DESC LIMIT 1
                """, ch["user_id"], ch["id"])

            if not last_confirm:
                continue  # челлендж еще не подтверждался ни разу

            last_local = last_confirm.astimezone(user_tz)
            days_missed = (user_now.date() - last_local.date()).days

            repeat_count = ch["repeat_count"] or 1

            # ⭐ 1 — без аннулирования
            if repeat_count == 1:
                continue

            # ⭐⭐ — сброс, если пропущено ≥ 2 дня подряд
            elif repeat_count == 2 and days_missed >= 2:
                await reset_challenge(pool, ch, reason="2 дня подряд без подтверждения")

            # ⭐⭐⭐ — сброс, если пропущен хотя бы 1 день
            elif repeat_count == 3 and days_missed >= 1:
                await reset_challenge(pool, ch, reason="1 день пропуска")


        print("✅ Проверка пропусков челленджей завершена")
        await asyncio.sleep(24 * 60 * 60)  # проверка 1 раз в сутки


async def reset_challenge(pool, ch, reason: str):
    """
    Удаляет челлендж из активных и уведомляет пользователя.
    """
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM habits WHERE id = $1", ch["id"])

    from aiogram import Bot
    from config import BOT_TOKEN
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(
            ch["user_id"],
            f"⚠️ Твой челлендж *{ch['name']}* аннулирован!\n"
            f"Причина: {reason}.\n\n"
            f"Не расстраивайся — начни заново и держи ритм 💪",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"⚠️ Ошибка при уведомлении {ch['user_id']}: {e}")
    finally:
        await bot.session.close()
