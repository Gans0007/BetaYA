from data.achievements_data import ALL_ACHIEVEMENTS
from repositories.achievements.achievements_repository import (
    has_user_achievement,
    grant_achievement,
)
from repositories.user_stats_repository import increment_xp

import logging

logger = logging.getLogger(__name__)


async def add_usdt_reward(conn, user_id: int, amount: float):
    await conn.execute("""
        UPDATE user_stats
        SET usdt_payments = usdt_payments + $1
        WHERE user_id = $2
    """, amount, user_id)


async def get_user_stats(conn, user_id: int):
    return await conn.fetchrow("""
        SELECT current_streak, total_confirmed_days
        FROM user_stats
        WHERE user_id = $1
    """, user_id)


def check_condition(stats, condition_type: str, condition_value: int) -> bool:
    if condition_type == "streak":
        return stats["current_streak"] >= condition_value
    if condition_type == "total_confirms":
        return stats["total_confirmed_days"] >= condition_value
    return False


async def get_category_progress(conn, user_id: int, category: str):
    """
    Возвращает прогресс пользователя по категории достижений.
    {
        "completed": int,
        "total": int
    }
    """

    from data.achievements_data import ALL_ACHIEVEMENTS
    from repositories.achievements.achievements_repository import get_user_achievements_codes

    # Все достижения категории
    category_achievements = ALL_ACHIEVEMENTS.get(category, [])
    total = len(category_achievements)

    if total == 0:
        return {"completed": 0, "total": 0}

    # Получаем коды достижений пользователя
    user_codes = await get_user_achievements_codes(conn, user_id)

    # Считаем выполненные
    completed = sum(
        1 for ach in category_achievements
        if ach["code"] in user_codes
    )

    return {
        "completed": completed,
        "total": total
    }


async def check_and_grant_achievements(conn, user_id: int):
    stats = await get_user_stats(conn, user_id)
    if not stats:
        return []

    newly_earned = []

    for category_achievements in ALL_ACHIEVEMENTS.values():
        for achievement in category_achievements:

            if not check_condition(stats, achievement["condition_type"], achievement["condition_value"]):
                continue

            if await has_user_achievement(conn, user_id, achievement["code"]):
                continue

            # Присвоение достижения
            await grant_achievement(conn, user_id, achievement["code"])

            logger.info(
                f"🏆 Достижение выдано | Пользователь: {user_id} | "
                f"Код: {achievement['code']} | "
                f"Название: {achievement['title']}"
            )

            # Начисление XP
            if achievement.get("xp_reward", 0) > 0:
                await increment_xp(conn, user_id, achievement["xp_reward"])

                logger.info(
                    f"⭐ Начислен XP | Пользователь: {user_id} | "
                    f"+{achievement['xp_reward']} XP за достижение "
                    f"'{achievement['title']}'"
                )

            # Начисление USDT
            if achievement.get("usdt_reward", 0) > 0:
                await add_usdt_reward(conn, user_id, achievement["usdt_reward"])

                logger.info(
                    f"💰 Начислен USDT | Пользователь: {user_id} | "
                    f"+{achievement['usdt_reward']} USDT за достижение "
                    f"'{achievement['title']}'"
                )

            newly_earned.append(achievement)

    return newly_earned