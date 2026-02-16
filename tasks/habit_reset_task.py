# habit_reset_task.py

import random
import asyncio
from datetime import datetime, timedelta
import pytz
from core.database import get_pool

from handlers.tone.habit_reset_tone import HABIT_RESET_TONE


async def check_habit_resets(bot):
    """
    Ежедневный сброс привычек:
      ⭐ Легко — без сбросов
      ⭐⭐ — сброс, если пропущено ≥ 2 дней
      ⭐⭐⭐ — сброс, если пропущено ≥ 1 дня

    Variant D:
      Если привычка была сброшена 3 раза подряд → is_active = FALSE
    """

    while True:
        pool = await get_pool()

        # Получаем всех пользователей с активными привычками
        async with pool.acquire() as conn:
            users = await conn.fetch("""
                SELECT DISTINCT u.user_id, u.timezone
                FROM users u
                JOIN habits h ON h.user_id = u.user_id
                WHERE h.is_challenge = FALSE AND h.is_active = TRUE
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

            # ближайшая полуночь
            next_reset_local = user_now.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            if next_reset_local <= user_now:
                next_reset_local += timedelta(days=1)

            next_reset_utc = next_reset_local.astimezone(pytz.utc)
            delay = (next_reset_utc - now_utc).total_seconds()

            asyncio.create_task(run_user_habit_reset(user_id, tz_str, delay, bot))

        await asyncio.sleep(24 * 60 * 60)


async def run_user_habit_reset(user_id: int, tz_str: str, delay: float, bot):
    """Сбрасывает привычки пользователя в его локальную полуночь."""
    await asyncio.sleep(delay)

    user_tz = pytz.timezone(tz_str)
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    user_now = now_utc.astimezone(user_tz)

    pool = await get_pool()

    # Берём активные привычки
    async with pool.acquire() as conn:
        habits = await conn.fetch("""
            SELECT h.id, h.name,
                   h.done_days,
                   h.difficulty,
                   h.reset_streak,
                   u.timezone, h.user_id
            FROM habits h
            JOIN users u ON u.user_id = h.user_id
            WHERE h.user_id = $1
              AND h.is_challenge = FALSE
              AND h.is_active = TRUE
        """, user_id)

    for hb in habits:

        # Последнее подтверждение
        async with pool.acquire() as conn:
            last_confirm = await conn.fetchval("""
                SELECT datetime FROM confirmations
                WHERE habit_id = $1
                ORDER BY datetime DESC LIMIT 1
            """, hb["id"])

        # если не подтверждалась ни разу → сброс НЕ делаем
        if not last_confirm:
            continue

        last_local = last_confirm.astimezone(user_tz)
        days_since = (user_now.date() - last_local.date()).days

        diff = hb["difficulty"]  # 1,2,3
        reset_streak = hb["reset_streak"]

        # ⭐ ЛЕГКО — никогда не сбрасывается
        if diff == 1:
            continue

        need_reset = False

        # ⭐⭐ — сброс, если ПРОШЛО >= 3 дней с последнего подтверждения
        # (это значит, что было минимум 2 полных дня без подтверждений)
        if diff == 2 and days_since >= 3:
            need_reset = True

        # ⭐⭐⭐ — сброс, если ВЧЕРА не было подтверждения
        elif diff == 3:
            yesterday = user_now.date() - timedelta(days=1)
            if last_local.date() != yesterday:
                need_reset = True

        if need_reset:
            await process_reset(pool, hb, reset_streak, bot)
        else:
            # если пользователь подтвердил → streak обнуляем
            await reset_streak_zero(pool, hb["id"])


async def process_reset(pool, hb, reset_streak, bot):
    """Обрабатываем сброс — без деактивации привычки"""

    habit_id = hb["id"]
    user_id = hb["user_id"]

    reset_streak += 1

    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE habits
            SET done_days = 0,
                reset_streak = $2
            WHERE id = $1
        """, habit_id, reset_streak)

    await send_reset_notification(user_id, hb["name"], reset_streak, bot)


async def reset_streak_zero(pool, habit_id):
    """Сбрасывает reset_streak, если человек подтвердил привычку"""
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE habits
            SET reset_streak = 0
            WHERE id = $1
        """, habit_id)


async def send_reset_notification(user_id, name, streak, bot):

    # 1. Берём тон пользователя
    pool = await get_pool()
    async with pool.acquire() as conn:
        tone = await conn.fetchval("""
            SELECT notification_tone FROM users WHERE user_id = $1
        """, user_id)

    # fallback — если по какой-то причине null
    if tone not in HABIT_RESET_TONE:
        tone = "friend"

    # 2. Рандомная цитата
    quote = random.choice(HABIT_RESET_TONE[tone])

    # 3. Формируем текст
    if tone == "friend":
        text = (
            f"⚠️ Привычка *{name}* была сброшена.\n"
            f"{quote}"
        )

    elif tone == "gamer":
        text = (
            f"🎮 Провал по привычке *{name}*.\n"
            f"{quote}"
        )

    elif tone == "spartan":
        text = (
            f"⚔️ Привычка *{name}* была сброшена.\n"
            f"Пропущено подряд: *{streak}*\n\n"
            f"{quote}"
        )

    try:
        await bot.send_message(user_id, text, parse_mode="Markdown")
    except Exception as e:
        print(f"⚠️ Ошибка отправки уведомления о сбросе привычки {habit_id}: {e}")



