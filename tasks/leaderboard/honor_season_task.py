# ==========================================
# tasks/leaderboard/honor_season_task.py
# ==========================================

import asyncio
import logging
from datetime import datetime, timezone

import asyncpg
import pytz

from core.database import get_pool
from core.shutdown import shutdown_event
from services.leaderboard.season_service import get_current_season_info


logger = logging.getLogger(__name__)


async def honor_season_rank_daily(bot):
    """
    Раз в сутки в 00:05 по Europe/Kyiv:

    1. Определяет текущий сезон.
    2. Создаёт сезонную запись для новых пользователей.
    3. Считает сезонный рейтинг по season_xp.
    4. Сравнивает старое и новое место.
    5. Отправляет уведомление пользователю.
    6. Сохраняет новые места в user_season_stats.
    """

    pool = await get_pool()

    while not shutdown_event.is_set():
        try:
            await process_season_ranking(bot, pool)

        except (
            asyncpg.exceptions.ConnectionDoesNotExistError,
            ConnectionResetError,
            OSError
        ) as error:
            logger.error(
                f"[HONOR SEASON ERROR] Потеряно соединение с БД: {error}"
            )

        except Exception as error:
            logger.exception(
                f"[HONOR SEASON UNEXPECTED ERROR] {error}"
            )

        try:
            await asyncio.wait_for(
                shutdown_event.wait(),
                timeout=60
            )
        except asyncio.TimeoutError:
            pass


async def process_season_ranking(bot, pool):
    """
    Выполняет один пересчёт сезонного рейтинга.
    """

    timezone_kyiv = pytz.timezone("Europe/Kyiv")

    now_utc = datetime.now(timezone.utc)
    local_time = now_utc.astimezone(timezone_kyiv)
    today = local_time.date()

    # Запускаем только в 00:05 по Киеву
    if not (
        local_time.hour == 0
        and local_time.minute == 5
    ):
        return

    season_info = get_current_season_info(today)

    season_key = season_info["key"]
    season_name = season_info["name"]
    season_end = season_info["end"]
    days_left = season_info["days_left"]

    async with pool.acquire() as conn:

        # ------------------------------------------
        # Создаём сезонные записи всем пользователям
        # ------------------------------------------
        await conn.execute("""
            INSERT INTO user_season_stats (
                user_id,
                season_key,
                season_xp
            )
            SELECT
                u.user_id,
                $1,
                0
            FROM users u

            ON CONFLICT (user_id, season_key)
            DO NOTHING
        """, season_key)

        # ------------------------------------------
        # Проверяем, выполнялся ли рейтинг сегодня
        # ------------------------------------------
        not_updated_count = await conn.fetchval("""
            SELECT COUNT(*)
            FROM user_season_stats
            WHERE season_key = $1
              AND last_rank_update IS DISTINCT FROM $2
        """, season_key, today)

        if not_updated_count == 0:
            return

        logger.info(
            f"[SEASON] Запуск пересчёта рейтинга {season_key}"
        )

        # ------------------------------------------
        # Получаем старые и новые места
        # ------------------------------------------
        ranked_users = await conn.fetch("""
            SELECT
                ss.user_id,
                ss.last_season_rank AS old_rank,

                ROW_NUMBER() OVER (
                    ORDER BY
                        COALESCE(ss.season_xp, 0) DESC,
                        ss.user_id ASC
                ) AS new_rank

            FROM user_season_stats ss

            WHERE ss.season_key = $1

            ORDER BY new_rank
        """, season_key)

    # ==========================================
    # Уведомления
    # ==========================================

    for user in ranked_users:
        user_id = user["user_id"]
        old_rank = user["old_rank"]
        new_rank = user["new_rank"]

        if new_rank is None:
            continue

        if old_rank is None:
            message = (
                f"🏆 <b>{season_name}</b>\n\n"
                f"Твоё стартовое место в сезонном рейтинге: "
                f"<b>{new_rank}</b>\n\n"
                f"До конца сезона: <b>{days_left} дн.</b>\n"
                f"Сезон закончится: <b>{season_end.strftime('%d.%m.%Y')}</b>"
            )

        else:
            delta = old_rank - new_rank

            if delta > 0:
                message = (
                    f"📈 <b>Ты поднялся в сезонном рейтинге!</b>\n\n"
                    f"Было место: <b>{old_rank}</b>\n"
                    f"Стало: <b>{new_rank}</b>\n\n"
                    f"Ты улучшил позицию на "
                    f"<b>{delta}</b> 🔥\n\n"
                    f"До конца сезона: <b>{days_left} дн.</b>"
                )

            elif delta < 0:
                message = (
                    f"📉 <b>Ты опустился в сезонном рейтинге.</b>\n\n"
                    f"Было место: <b>{old_rank}</b>\n"
                    f"Стало: <b>{new_rank}</b>\n\n"
                    f"Потеряно позиций: "
                    f"<b>{abs(delta)}</b>\n\n"
                    f"До конца сезона: <b>{days_left} дн.</b>"
                )

            else:
                message = (
                    f"➡️ <b>Сезонный рейтинг</b>\n\n"
                    f"Ты сохранил своё место: "
                    f"<b>{new_rank}</b>\n\n"
                    f"До конца сезона: <b>{days_left} дн.</b>"
                )

        try:
            await bot.send_message(
                chat_id=user_id,
                text=message,
                disable_notification=True,
                parse_mode="HTML"
            )

            logger.info(
                f"[SEASON] Уведомление отправлено пользователю {user_id}"
            )

            await asyncio.sleep(0.1)

        except Exception as error:
            logger.error(
                f"[SEASON SEND ERROR] "
                f"Пользователь {user_id}: {error}"
            )

    # ==========================================
    # Сохраняем новые места
    # ==========================================

    async with pool.acquire() as conn:
        await conn.execute("""
            WITH ranked AS (
                SELECT
                    ss.user_id,

                    ROW_NUMBER() OVER (
                        ORDER BY
                            COALESCE(ss.season_xp, 0) DESC,
                            ss.user_id ASC
                    ) AS new_rank

                FROM user_season_stats ss

                WHERE ss.season_key = $1
            )

            UPDATE user_season_stats ss

            SET
                last_season_rank = ranked.new_rank,
                last_rank_update = $2,
                updated_at = NOW()

            FROM ranked

            WHERE ss.user_id = ranked.user_id
              AND ss.season_key = $1
        """, season_key, today)

    logger.info(
        f"[SEASON] Рейтинг {season_key} успешно обновлён"
    )