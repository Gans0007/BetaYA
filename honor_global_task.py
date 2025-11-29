# ================================
#  honor_global_task.py
# ================================

import asyncio
from database import get_pool
from services.honor_global_service import get_global_rank
from datetime import datetime, timezone
import pytz
import logging

logger = logging.getLogger(__name__)


async def honor_global_rank_daily(bot):
    """
    Запускается в фоне, проверяет каждую минуту локальное время пользователя.
    В 00:05 вызывает перерасчёт рейтинга.
    """
    while True:
        await process_all_users(bot)
        await asyncio.sleep(60)


async def process_all_users(bot):
    pool = await get_pool()
    now_utc = datetime.now(timezone.utc)

    async with pool.acquire() as conn:
        users = await conn.fetch("""
            SELECT user_id, timezone, last_global_rank, last_rank_update
            FROM users
            WHERE timezone IS NOT NULL
        """)

    for u in users:
        await process_user_rank(bot, u, now_utc)


async def process_user_rank(bot, user, now_utc):
    user_id = user["user_id"]
    tz_name = user["timezone"] or "Europe/Kyiv"
    last_rank = user["last_global_rank"]
    last_date = user["last_rank_update"]

    try:
        tz = pytz.timezone(tz_name)
    except:
        tz = pytz.timezone("Europe/Kyiv")

    local_time = now_utc.astimezone(tz)
    today = local_time.date()

    # Не время — выходим
    if not (local_time.hour == 0 and local_time.minute == 5):
        return

    # Уже проверяли сегодня — выходим
    if last_date == today:
        return

    # Считаем глобальное место
    rank = await get_global_rank(user_id)
    if rank is None:
        return

    # Обновляем в БД
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET last_global_rank = $2,
                last_rank_update = $3
            WHERE user_id = $1
        """, user_id, rank, today)

    # Если первый раз — не уведомляем
    if last_rank is None:
        logger.info(f"[GLOBAL] Пользователь {user_id}: первое вычисление места {rank}")
        return

    # Сравниваем разницу
    delta = last_rank - rank

    # Улучшение (место выросло)
    if delta > 0:
        await bot.send_message(
            user_id,
            f"📈 Ты поднялся в глобальном рейтинге!\n"
            f"Было место: {last_rank}\n"
            f"Стало: {rank}\n"
            f"Ты улучшил позицию на {delta}!"
        )
        logger.info(f"[GLOBAL] {user_id} улучшил место {last_rank} → {rank} (+{delta})")

    # Ухудшение
    elif delta < 0:
        delta = abs(delta)
        await bot.send_message(
            user_id,
            f"📉 Ты немного просел в глобальном рейтинге.\n"
            f"Было место: {last_rank}\n"
            f"Стало: {rank}\n"
            f"Потерял {delta} позиций."
        )
        logger.info(f"[GLOBAL] {user_id} упал {last_rank} → {rank} (-{delta})")

    else:
        logger.info(f"[GLOBAL] {user_id} место не изменилось: {rank}")
