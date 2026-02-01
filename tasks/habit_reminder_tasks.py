# =======================================
# 🔔 Habit Reminder Task
# =======================================

import asyncio
from datetime import datetime, timezone
import pytz
import logging
import asyncpg

from aiogram import Bot
from database import get_pool
from core.shutdown import shutdown_event

logger = logging.getLogger(__name__)

# ВВЕРХУ ФАЙЛА
LAST_SENT = set()

async def habit_reminder_task(bot: Bot):
    """
    Проверяет каждую минуту:
    - локальное время пользователя
    - habits.reminder_time
    Отправляет напоминание ровно в HH:MM
    """

    pool = await get_pool()

    while not shutdown_event.is_set():
        try:
            await process_all_reminders(bot, pool)

        except (asyncpg.exceptions.ConnectionDoesNotExistError,
                ConnectionResetError,
                OSError) as e:
            logger.error(f"[HABIT REMINDER ERROR] DB connection lost: {e}")

        except Exception as e:
            logger.error(f"[HABIT REMINDER UNEXPECTED ERROR] {e}", exc_info=True)

        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=60)
        except asyncio.TimeoutError:
            pass


async def process_all_reminders(bot: Bot, pool):
    # Берём текущее UTC-время ОДИН РАЗ за проход
    now_utc = datetime.now(timezone.utc)

    # 🧹 Очистка LAST_SENT от прошлых дней
    today = now_utc.date()
    LAST_SENT.difference_update(
        {key for key in LAST_SENT if key[2] != today}
    )

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                h.id AS habit_id,
                h.name,
                h.user_id,
                h.reminder_time,
                u.timezone
            FROM habits h
            JOIN users u ON u.user_id = h.user_id
            WHERE
                h.is_active = TRUE
                AND h.reminder_time IS NOT NULL
        """)

    for row in rows:
        await process_single_reminder(bot, row, now_utc)


async def process_single_reminder(bot: Bot, row, now_utc):
    habit_id = row["habit_id"]
    habit_name = row["name"]
    user_id = row["user_id"]
    reminder_time = row["reminder_time"]
    tz_name = row["timezone"] or "Europe/Kyiv"

    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = pytz.timezone("Europe/Kyiv")

    local_time = now_utc.astimezone(tz)
    
    # 🔥 Сравнение ТОЛЬКО по локальному часу и минуте
    if (
        local_time.hour != reminder_time.hour
        or local_time.minute != reminder_time.minute
    ):
        return


    # 🔒 Защита от повторной отправки в день
    key = (user_id, habit_id, local_time.date())
    if key in LAST_SENT:
        return

    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"🔔 Напоминание\n\n"
                f"⚡️ Пора выполнить привычку:\n"
                f"*{habit_name}*"
            ),
            parse_mode="Markdown",
            disable_notification=False
        )

        LAST_SENT.add(key)

        logger.info(
            f"[REMINDER SENT] Напоминание пользователю {user_id} "
            f"в {local_time.strftime('%H:%M:%S')} ({tz.zone}) отправлено"
        )

    except Exception as e:
        logger.error(f"[HABIT REMINDER SEND ERROR] user={user_id}: {e}")