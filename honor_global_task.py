# ================================
#  honor_global_task.py
# ================================

import asyncio
from datetime import datetime, timezone
import pytz
import logging
import asyncpg

from database import get_pool
from services.honor_global_service import get_global_rank
from core.shutdown import shutdown_event

logger = logging.getLogger(__name__)


async def honor_global_rank_daily(bot):
    """
    Запускается в фоне, проверяет каждую минуту локальное время пользователя.
    В 00:05 вызывает перерасчёт рейтинга.
    """

    pool = await get_pool()

    while not shutdown_event.is_set():
        try:
            await process_all_users(bot, pool)

        except (asyncpg.exceptions.ConnectionDoesNotExistError,
                ConnectionResetError,
                OSError) as e:
            logger.error(f"[HONOR GLOBAL ERROR] Потеряно соединение с БД: {e}")

        except Exception as e:
            logger.error(f"[HONOR GLOBAL UNEXPECTED ERROR] {e}")

        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=60)
        except asyncio.TimeoutError:
            pass


async def process_all_users(bot, pool):
    now_utc = datetime.now(timezone.utc)

    async with pool.acquire() as conn:
        users = await conn.fetch("""
            SELECT user_id, timezone, last_global_rank, last_rank_update
            FROM users
            WHERE timezone IS NOT NULL
        """)

    for u in users:
        await process_user_rank(bot, u, now_utc, pool)


async def process_user_rank(bot, user, now_utc, pool):
    user_id = user["user_id"]
    tz_name = user["timezone"] or "Europe/Kyiv"
    last_rank = user["last_global_rank"]
    last_date = user["last_rank_update"]

    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = pytz.timezone("Europe/Kyiv")

    local_time = now_utc.astimezone(tz)
    today = local_time.date()

    if not (local_time.hour == 0 and local_time.minute == 5):
        return

    if last_date == today:
        return

    logger.info(f"[GLOBAL] Запуск расчёта рейтинга для user_id={user_id}")

    rank = await get_global_rank(user_id)
    if rank is None:
        return

    # ======= 1) Первая отправка =======
    if last_rank is None:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=(
                    f"🏁 Твоё стартовое место в глобальном рейтинге: {rank}\n"
                    f"Теперь каждый день ты будешь видеть свой прогресс 💪"
                ),
                disable_notification=True,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"[GLOBAL SEND ERROR] юзеру {user_id}: {e}")

        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE users
                SET last_global_rank = $2,
                    last_rank_update = $3
                WHERE user_id = $1
            """, user_id, rank, today)

        return

    # ======= 2) Сравниваем =======
    delta = last_rank - rank

    if delta > 0:
        msg = (
            f"📈 Ты поднялся в глобальном рейтинге!\n"
            f"Было место: {last_rank}\n"
            f"Стало: {rank}\n"
            f"Ты улучшил позицию на {delta}! 🔥"
        )
    elif delta < 0:
        msg = (
            f"📉 Ты немного просел в глобальном рейтинге.\n"
            f"Было место: {last_rank}\n"
            f"Стало: {rank}\n"
            f"Ты потерял {abs(delta)} позиций."
        )
    else:
        msg = (
            f"➡ Ты сохранил своё место в рейтинге: {rank}\n"
            f"Стабильность — уже результат 💪"
        )

    try:
        await bot.send_message(
            chat_id=user_id,
            text=msg,
            disable_notification=True,
            parse_mode="HTML"
        )
        logger.info(f"[GLOBAL] уведомление отправлено юзеру {user_id}")
        await asyncio.sleep(0.1)

    except Exception as e:
        logger.error(f"[GLOBAL SEND ERROR] юзеру {user_id}: {e}")

    # ======= 3) Обновляем БД =======
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET last_global_rank = $2,
                last_rank_update = $3
            WHERE user_id = $1
        """, user_id, rank, today)
