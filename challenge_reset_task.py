import asyncio
from datetime import datetime, timedelta
import pytz
from database import get_pool


async def check_challenge_resets():
    """
    Раз в сутки (в 00:00 по локальному времени пользователя)
    проверяет пропуски челленджей и сбрасывает сделанные дни (done_days = 0)
    в зависимости от количества завершений (repeat_count).
    ⭐ 1 — никогда не сбрасывается
    ⭐⭐ — если пропущено >= 2 дней
    ⭐⭐⭐ — если пропущено >= 1 дня
    """

    while True:
        pool = await get_pool()

        async with pool.acquire() as conn:
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

            user_now = now_utc.astimezone(user_tz)

            # ближайшая локальная полуночь
            next_reset_local = user_now.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            # если уже прошла — переносим на завтра
            if next_reset_local <= user_now:
                next_reset_local += timedelta(days=1)

            next_reset_utc = next_reset_local.astimezone(pytz.utc)
            delay = (next_reset_utc - now_utc).total_seconds()

            asyncio.create_task(run_user_reset(user_id, tz_str, delay))

        # обновлять список юзеров раз в день
        await asyncio.sleep(24 * 60 * 60)


async def run_user_reset(user_id: int, tz_str: str, delay: float):
    """Дождаться локальной полуночи пользователя и выполнить сброс."""
    await asyncio.sleep(delay)

    user_tz = pytz.timezone(tz_str)
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    user_now = now_utc.astimezone(user_tz)

    pool = await get_pool()

    async with pool.acquire() as conn:
        challenges = await conn.fetch("""
            SELECT h.id, h.name, h.challenge_id,
                   h.days, h.done_days,
                   c.repeat_count,
                   u.timezone, h.user_id
            FROM habits h
            JOIN completed_challenges c ON c.challenge_id = h.challenge_id
            JOIN users u ON u.user_id = h.user_id
            WHERE h.user_id = $1
              AND h.is_challenge = TRUE
              AND h.is_active = TRUE
        """, user_id)

    for ch in challenges:

        async with pool.acquire() as conn:
            last_confirm = await conn.fetchval("""
                SELECT datetime FROM confirmations
                WHERE habit_id = $1
                ORDER BY datetime DESC LIMIT 1
            """, ch["id"])

        if not last_confirm:
            continue  # челлендж ещё ни разу не подтверждался

        last_local = last_confirm.astimezone(user_tz)
        days_since = (user_now.date() - last_local.date()).days

        repeat = ch["repeat_count"]  # 1..3

        # ⭐1 — новичок, не сбрасываем
        if repeat == 1:
            continue

        # ⭐⭐ — сброс, если прошло >= 3 дней с последнего подтверждения
        # (то есть было минимум 2 полных дня без подтверждений)
        if repeat == 2 and days_since >= 3:
            await reset_challenge_progress(pool, ch, "2 дня без подтверждения")

        # ⭐⭐⭐ — сброс, если вчера не было подтверждения
        elif repeat == 3:
            yesterday = user_now.date() - timedelta(days=1)
            if last_local.date() != yesterday:
                await reset_challenge_progress(pool, ch, "1 день пропуска")


async def reset_challenge_progress(pool, ch, reason: str):
    """Сбрасывает прогресс челленджа без удаления."""
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
            f"Но это часть пути. Продолжай дальше 💪",
            parse_mode="Markdown"
        )
    except Exception as e:
        print("Ошибка отправки уведомления:", e)
    finally:
        await bot.session.close()
