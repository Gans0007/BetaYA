# ================================
#  honor_global_task.py
# ================================

import asyncio
from datetime import datetime, timezone
import pytz
import logging
import asyncpg

from core.database import get_pool
from core.shutdown import shutdown_event

logger = logging.getLogger(__name__)


async def honor_global_rank_daily(bot):
    """
    Раз в сутки в 00:05 по Europe/Kyiv:
    1. Считает новый глобальный рейтинг всем пользователям
    2. Сравнивает старое место с новым
    3. Отправляет уведомление о повышении / понижении / сохранении места
    4. Одним общим обновлением записывает новые места в БД
    """

    pool = await get_pool()

    while not shutdown_event.is_set():
        try:
            await process_global_ranking(bot, pool)

        except (
            asyncpg.exceptions.ConnectionDoesNotExistError,
            ConnectionResetError,
            OSError
        ) as e:
            logger.error(f"[HONOR GLOBAL ERROR] Потеряно соединение с БД: {e}")

        except Exception as e:
            logger.error(f"[HONOR GLOBAL UNEXPECTED ERROR] {e}")

        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=60)
        except asyncio.TimeoutError:
            pass


async def process_global_ranking(bot, pool):
    tz = pytz.timezone("Europe/Kyiv")

    now_utc = datetime.now(timezone.utc)
    local_time = now_utc.astimezone(tz)
    today = local_time.date()

    # Запуск только в 00:05
    if not (local_time.hour == 0 and local_time.minute == 5):
        return

    async with pool.acquire() as conn:

        # Если сегодня уже всем обновили рейтинг — не запускаем повторно
        not_updated_count = await conn.fetchval("""
            SELECT COUNT(*)
            FROM users
            WHERE last_rank_update IS DISTINCT FROM $1
        """, today)

        if not_updated_count == 0:
            return

        logger.info("[GLOBAL] Запуск общего пересчёта рейтинга")

        ranked_users = await conn.fetch("""
            SELECT
                u.user_id,
                u.last_global_rank AS old_rank,
                ROW_NUMBER() OVER (
                    ORDER BY COALESCE(s.xp, 0) DESC, u.user_id ASC
                ) AS new_rank
            FROM users u
            LEFT JOIN user_stats s ON s.user_id = u.user_id
            ORDER BY new_rank
        """)

    # ======= 1) УВЕДОМЛЕНИЯ =======

    for user in ranked_users:
        user_id = user["user_id"]
        old_rank = user["old_rank"]
        new_rank = user["new_rank"]

        if new_rank is None:
            continue

        # Первая отправка
        if old_rank is None:
            msg = (
                f"🏁 Твоё стартовое место в глобальном рейтинге: {new_rank}\n"
                f"Теперь каждый день ты будешь видеть свой прогресс 💪"
            )

        else:
            delta = old_rank - new_rank

            if delta > 0:
                msg = (
                    f"📈 Ты поднялся в глобальном рейтинге!\n"
                    f"Было место: {old_rank}\n"
                    f"Стало: {new_rank}\n"
                    f"Ты улучшил позицию на {delta}! 🔥"
                )

            elif delta < 0:
                msg = (
                    f"📉 Ты немного просел в глобальном рейтинге.\n"
                    f"Было место: {old_rank}\n"
                    f"Стало: {new_rank}\n"
                    f"Ты потерял {abs(delta)} позиций."
                )

            else:
                msg = (
                    f"➡ Ты сохранил своё место в рейтинге: {new_rank}\n"
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

    # ======= 2) ОБНОВЛЯЕМ РЕЙТИНГ ВСЕМ СРАЗУ =======

    async with pool.acquire() as conn:
        await conn.execute("""
            WITH ranked AS (
                SELECT
                    u.user_id,
                    ROW_NUMBER() OVER (
                        ORDER BY COALESCE(s.xp, 0) DESC, u.user_id ASC
                    ) AS new_rank
                FROM users u
                LEFT JOIN user_stats s ON s.user_id = u.user_id
            )
            UPDATE users u
            SET
                last_global_rank = ranked.new_rank,
                last_rank_update = $1
            FROM ranked
            WHERE u.user_id = ranked.user_id
        """, today)

    logger.info("[GLOBAL] общий рейтинг успешно обновлён")