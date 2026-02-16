# services/user_stats_service.py

import logging
from repositories.user_stats_repository import (
    increment_finished_habits as repo_inc_habits,
    increment_finished_challenges as repo_inc_challenges,
    increment_total_stars as repo_inc_stars,
)

logger = logging.getLogger(__name__)


async def increment_finished_habits(conn, user_id: int):
    await repo_inc_habits(conn, user_id)
    logger.info(f"[STATS] +1 finished_habits user={user_id}")


async def increment_finished_challenges(conn, user_id: int):
    await repo_inc_challenges(conn, user_id)
    logger.info(f"[STATS] +1 finished_challenges user={user_id}")


async def increment_total_stars(conn, user_id: int, stars: int):
    if stars <= 0:
        return

    await repo_inc_stars(conn, user_id, stars)
    logger.info(f"[STATS] +{stars} ⭐ user={user_id}")
