# daily_reminder_task.py
import asyncio
import random
from datetime import datetime, timedelta
import pytz
from database import get_pool
from aiogram import Bot

REMINDER_MESSAGES = [
    "💪 Напоминаю о твоих привычках/челленджах! Сделай сегодня хотя бы одно действие!",
    "🔥 Маленькое действие сегодня — большой результат завтра! Подтверди прогресс по привычке/челленджу.",
    "🚀 Ещё есть время подтвердить выполнение. Поехали!",
    "🏁 Не откладывай — сегодня отличный день для прогресса!",
    "✨ Держи ритм! Подтверди хотя бы одну задачу сегодня!"
]


async def send_daily_reminders(bot: Bot):
    """
    Раз в сутки планирует ОДНО случайное напоминание для каждого пользователя
    (между 12:00 и 20:00 по его таймзоне), если у него есть активные привычки/челленджи.
    """
    pool = await get_pool()

    while True:
        # Берём пользователей, у кого есть активные записи (и привычки, и челленджи)
        async with pool.acquire() as conn:
            users = await conn.fetch("""
                SELECT DISTINCT u.user_id, u.timezone
                FROM users u
                JOIN habits h ON h.user_id = u.user_id
                WHERE h.is_active = TRUE
            """)

        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)

        for user in users:
            user_id = user["user_id"]
            tz_str = user["timezone"] or "Europe/Kyiv"

            try:
                user_tz = pytz.timezone(tz_str)
            except Exception:
                user_tz = pytz.timezone("Europe/Kyiv")

            user_now = now_utc.astimezone(user_tz)

            # 🎲 случайное локальное время 12:00–20:59
            random_hour = random.randint(12, 20)
            random_minute = random.randint(0, 59)
            next_run_local = user_now.replace(
                hour=random_hour, minute=random_minute, second=0, microsecond=0
            )
            if next_run_local < user_now:
                next_run_local += timedelta(days=1)

            # в UTC для sleep
            next_run_utc = next_run_local.astimezone(pytz.utc)
            delay = (next_run_utc - now_utc).total_seconds()

            # Лог планирования
            print(
                f"📅 Пользователь {user_id} ({tz_str}) — "
                f"напоминание запланировано на {next_run_local.strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # планируем индивидуальную отправку
            asyncio.create_task(
                schedule_user_reminder(bot, user_id, delay, tz_str)
            )

        # через сутки перепланируем новое случайное время
        await asyncio.sleep(24 * 60 * 60)


async def schedule_user_reminder(bot: Bot, user_id: int, delay: float, tz_str: str):
    """Отложенная отправка напоминания одному пользователю в его локальное время."""
    await asyncio.sleep(delay)
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Есть ли ХОТЯ БЫ ОДНА активная задача (привычка или челлендж) без подтверждения СЕГОДНЯ в локальной TZ
        rows = await conn.fetch("""
            SELECT h.id
            FROM habits h
            LEFT JOIN confirmations c
                   ON h.id = c.habit_id
                  AND (c.datetime AT TIME ZONE $2)::date = (NOW() AT TIME ZONE $2)::date
            WHERE h.user_id = $1
              AND h.is_active = TRUE
              AND c.id IS NULL
            LIMIT 1
        """, user_id, tz_str)

        if not rows:
            # Всё уже подтверждено сегодня — молчим
            return

    try:
        text = random.choice(REMINDER_MESSAGES)
        await bot.send_message(user_id, text)
        print(
            f"📨 Отправлено напоминание пользователю {user_id} "
            f"({tz_str}) в {datetime.now(pytz.timezone(tz_str)).strftime('%H:%M:%S')}"
        )
    except Exception as e:
        print(f"⚠️ Ошибка при отправке напоминания пользователю {user_id}: {e}")
