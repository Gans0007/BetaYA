from data.achievements_data import ALL_ACHIEVEMENTS

from repositories.achievements.achievements_repository import (
    grant_achievement,
    get_user_achievements_codes,
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
        SELECT
            current_streak,
            total_confirmed_days,
            usdt_payments
        FROM user_stats
        WHERE user_id = $1
    """, user_id)




async def check_condition(conn, user_id, stats, condition_type, condition_value):

    # 🔥 Стрик  confirm_habit_handler
    if condition_type == "streak":
        return stats["current_streak"] >= condition_value

    # 🔥 Общее количество подтверждений confirm_habit_handler
    if condition_type == "total_confirms":
        return stats["total_confirmed_days"] >= condition_value

    # 🔥 Завершение конкретного челленджа confirm_habit_handler
    if condition_type == "challenge_complete":

        result = await conn.fetchrow("""
            SELECT 1
            FROM completed_challenges
            WHERE user_id = $1
              AND challenge_id = $2
        """, user_id, condition_value)

        return result is not None

    # 💰 Количество приглашённых рефералов  start.py
    if condition_type == "referrals_count":
        result = await conn.fetchval("""
            SELECT COUNT(*)
            FROM referrals
            WHERE affiliate_id = $1
        """, user_id)

        logger.info(
            f"💰 Проверка referrals_count | user={user_id} | "
            f"count={result} | нужно={condition_value}"
        )

        return (result or 0) >= condition_value

    # 🟢 Количество активных рефералов
    if condition_type == "active_referrals":

        result = await conn.fetchval("""
            SELECT COUNT(*)
            FROM referrals
            WHERE affiliate_id = $1
              AND is_active = TRUE
        """, user_id)

        logger.info(
            f"🟢 Проверка active_referrals | user={user_id} | "
            f"active={result} | нужно={condition_value}"
        )

        return (result or 0) >= condition_value


    # 🏅 Уровень партнёра
    if condition_type == "referral_level":

        from services.affiliate_service import affiliate_service

        current_level, _, _ = await affiliate_service.get_affiliate_level_info(user_id)

        logger.info(
            f"🏅 Проверка referral_level | user={user_id} | "
            f"current={current_level['key']} | нужно={condition_value}"
        )

        return current_level["key"] == condition_value


    # 💵 Баланс USDT (берём из user_stats.usdt_payments)
    if condition_type == "usdt_balance":
        balance = stats.get("usdt_payments") or 0

        logger.info(
            f"💵 Проверка usdt_balance | user={user_id} | "
            f"balance={balance} | нужно={condition_value}"
        )

        return float(balance) >= float(condition_value)

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


async def check_and_grant_achievements(
    conn,
    user_id: int,
    trigger_types: list[str] | None = None
):
    logger.info(
        f"🔍 Проверка достижений для пользователя {user_id} | "
        f"trigger={trigger_types}"
    )

    stats = await get_user_stats(conn, user_id)
    if not stats:
        return []

    # ✅ 1 запрос в БД: получаем все ачивки пользователя
    user_codes = await get_user_achievements_codes(conn, user_id)

    newly_earned = []

    for category_achievements in ALL_ACHIEVEMENTS.values():
        for achievement in category_achievements:

            condition_type = achievement["condition_type"]

            # 🎯 Если передан trigger — фильтруем по типу условия
            if trigger_types and condition_type not in trigger_types:
                continue

            code = achievement["code"]

            # ✅ Уже есть — вообще ничего не проверяем (и не логируем лишнее)
            if code in user_codes:
                continue

            # ✅ Проверяем условие только если ачивки ещё нет
            if not await check_condition(
                conn,
                user_id,
                stats,
                condition_type,
                achievement["condition_value"]
            ):
                continue

            await grant_achievement(conn, user_id, code)

            # ✅ Обновляем кэш, чтобы в этом же прогоне не выдать повторно
            user_codes.add(code)

            logger.info(
                f"🏆 Достижение выдано | Пользователь: {user_id} | "
                f"Код: {code}"
            )

            if achievement.get("xp_reward", 0) > 0:
                await increment_xp(conn, user_id, achievement["xp_reward"])

            if achievement.get("usdt_reward", 0) > 0:
                await add_usdt_reward(
                    conn,
                    user_id,
                    achievement["usdt_reward"]
                )

            newly_earned.append(achievement)

    return newly_earned

async def process_achievements_and_notify(
    bot,
    conn,
    user_id: int,
    trigger_types: list[str] | None = None
):
    logger.info(
        f"📢 Отправка уведомлений | user={user_id} | "
        f"trigger={trigger_types}"
    )

    new_achievements = await check_and_grant_achievements(
        conn,
        user_id,
        trigger_types=trigger_types
    )

    for ach in new_achievements:

        text = (
            "🏆 Новое достижение!\n\n"
            f"{ach.get('icon', '🏆')} {ach['title']}\n"
            f"{ach['description']}\n\n"
            f"+{ach.get('xp_reward', 0)} XP"
        )

        if ach.get("usdt_reward", 0) > 0:
            text += f"\n+{ach['usdt_reward']} USDT"

        try:
            await bot.send_message(user_id, text)
        except Exception as e:
            logger.error(f"❗ Ошибка отправки уведомления: {e}")

    return new_achievements