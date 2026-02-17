# services/user_stats_service.py
import logging

from repositories.user_stats_repository import (
    increment_finished_habits as repo_inc_habits,
    increment_finished_challenges as repo_inc_challenges,
    increment_total_stars as repo_inc_stars,
    set_total_confirmed_days as repo_set_days,
    update_user_streak as repo_update_streak
)

logger = logging.getLogger(__name__)


# ===============================
# 📌 +1 завершённая привычка
# ===============================
async def increment_finished_habits(conn, user_id: int):
    await repo_inc_habits(conn, user_id)
    logger.info(f"[СТАТИСТИКА] Пользователь {user_id} завершил привычку (+1).")


# ===============================
# 📌 +1 завершённый челлендж
# ===============================
async def increment_finished_challenges(conn, user_id: int):
    await repo_inc_challenges(conn, user_id)
    logger.info(f"[СТАТИСТИКА] Пользователь {user_id} завершил челлендж (+1).")


# ===============================
# ⭐ +N звёзд
# ===============================
async def increment_total_stars(conn, user_id: int, stars: int):
    if stars <= 0:
        logger.warning(
            f"[СТАТИСТИКА] Попытка начислить некорректное количество звёзд: {stars} user={user_id}"
        )
        return

    await repo_inc_stars(conn, user_id, stars)
    logger.info(f"[СТАТИСТИКА] Пользователю {user_id} начислено {stars} ⭐.")


# ===============================
# 📅 Обновить общее количество дней
# ===============================
async def set_total_confirmed_days(conn, user_id: int, total_days: int):
    if total_days < 0:
        logger.warning(
            f"[СТАТИСТИКА] Попытка установить отрицательное количество дней: {total_days} user={user_id}"
        )
        return

    await repo_set_days(conn, user_id, total_days)
    logger.info(
        f"[СТАТИСТИКА] Пользователь {user_id} → всего подтверждённых дней: {total_days}"
    )


# ===============================
# 🔥 Обновить текущий стрик
# ===============================
async def update_user_streak(conn, user_id: int):
    new_streak = await repo_update_streak(conn, user_id)

    logger.info(
        f"[СТАТИСТИКА] Пользователь {user_id} → новый стрик: {new_streak}"
    )

    return new_streak