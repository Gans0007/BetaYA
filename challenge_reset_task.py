# challenge_reset_task.py
import asyncio
from datetime import datetime, timedelta, time
import pytz
from database import get_pool


async def check_challenge_resets():
    """
    Раз в сутки (в 00:00 каждого пользователя) проверяет пропуски челленджей
    и сбрасывает прогресс (done_days = 0) в зависимости от звезды.
    ⭐ 1 — не сбрасывается
    ⭐⭐ — если пропущено >= 2 дней
    ⭐⭐⭐ — если пропущено >= 1 дня
    """
    while True:
        pool = await get_pool()

        async with pool.acquire() as conn:
            # Берём всех пользователей с активными челленджами
            users = await conn.fetch("""
                SELECT DISTINCT u.user_id, u.timezone
                FROM users u
                JOIN habits h ON h.user_id = u.user_id
                WHERE h.is_challenge = TRUE AND h.is_active = TRUE
            """)

        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)

        for user in users:
            user_id = user["user_id"]
            tz_str = user["timezone"] or "Europe/Kyiv"
            try:
                user_tz = pytz.timezone(tz_str)
            except:
                user_tz = pytz.timezone("Europe/Kyiv")

            # локальное время пользователя
            user_now = now_utc.astimezone(user_tz)

            # следующая полуночь
            next_reset_local = user_now.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            if next_reset_local <= user_now:
                next_reset_local += timedelta(days=1)

            # переводим в UTC для asyncio.sleep()
            next_reset_utc = next_reset_local.astimezone(pytz.utc)
            delay = (next_reset_utc - now_utc).total_seconds()

            # запускаем индивидуальную задачу резета
            asyncio.create_task(run_user_reset(user_id, tz_str, delay))

        # перезапускаем поиск сутками
        await asyncio.sleep(24 * 60 * 60)


async def run_user_reset(user_id: int, tz_str: str, delay: float):
    """Ждёт локальную 00:00 и запускает сброс челленджей пользователя."""
    await asyncio.sleep(delay)

    pool = await get_pool()

    # выясняем какие челленджи активны у пользователя
    async with pool.acquire() as conn:
        challenges = await conn.fetch("""
            SELECT h.id, h.name, h.challenge_id, h.days, h.done_days,
                   c.repeat_count, u.timezone
            FROM habits h
            JOIN completed_challenges c ON c.challenge_id = h.challenge_id
            JOIN users u ON u.user_id = h.user_id
            WHERE h.user_id = $1 AND h.is_challenge = TRUE AND h.is_active = TRUE
        """, user_id)

    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    user_tz = pytz.timezone(tz_str)
    user_now = now_utc.astimezone(user_tz)

    for ch in challenges:
        # получаем последнее подтверждение
        async with pool.acquire() as conn:
            last_confirm = await conn.fetchval("""
                SELECT datetime FROM confirmations
                WHERE habit_id = $1
                ORDER BY datetime DESC LIMIT 1
            """, ch["id"])

        if not last_confirm:
            # ни разу не делал — пропуск не считаем
            continue

        last_local = last_confirm.astimezone(user_tz)

        # считаем пропущенные дни
        days_missed = (user_now.date() - last_local.date()).days

        repeat_count = ch["repeat_count"]

        # ⭐ правила
        if repeat_count == 1:
            continue  # новички не сбрасываются

        elif repeat_count == 2 and days_missed >= 2:
            await reset_challenge_progress(pool, ch, "2 дня без подтверждения")

        elif repeat_count == 3 and days_missed >= 1:
            await reset_challenge_progress(pool, ch, "1 день пропуска")


async def reset_challenge_progress(pool, ch, reason: str):
    """Обнуляет прогресс челленджа без удаления."""
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE habits
            SET done_days = 0
            WHERE id = $1
        """, ch["id"])

    from aiogram import Bot
    from config import BOT_TOKEN
    bot = Bot(token=BOT_TOKEN)

    try:
        await bot.send_message(
            ch["user_id"],
            f"⚠️ Прогресс по челленджу *{ch['name']}* был сброшен!\n"
            f"Причина: {reason}\n\n"
            f"Продолжай — у тебя всё получится 💪",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")
    finally:
        await bot.session.close()
