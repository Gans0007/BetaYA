# services/user_service.py
from datetime import date, timedelta
from core.database import get_pool

# -------------------------------
# 🔗 Связка репозиториев для пересчёта дней
# -------------------------------
from repositories.confirmations_repository import count_unique_confirm_days
from repositories.user_repository import update_total_confirmed_days
from services.user_stats_service import set_total_confirmed_days

# -------------------------------
# 🔁 Пересчёт и сохранение уникальных дней
# -------------------------------
async def recalculate_total_confirmed_days(conn, user_id: int) -> int:
    total = await count_unique_confirm_days(conn, user_id)
    await set_total_confirmed_days(conn, user_id, total)
    return total


# -------------------------------
# 🔥 Стрик: подсчёт текущего и максимального
# -------------------------------
async def update_user_streak(user_id: int):
    pool = await get_pool()

    async with pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT current_streak, max_streak, last_streak_date
            FROM users
            WHERE user_id = $1
        """, user_id)

        today = date.today()

        # Первый день когда пользователь подтверждает
        if user["last_streak_date"] is None:
            await conn.execute("""
                UPDATE users
                SET current_streak = 1,
                    max_streak = 1,
                    last_streak_date = $1
                WHERE user_id = $2
            """, today, user_id)
            return

        last_date = user["last_streak_date"]

        # Подтвердил подряд
        if last_date == today - timedelta(days=1):
            new_current = user["current_streak"] + 1
            new_max = max(new_current, user["max_streak"])

            await conn.execute("""
                UPDATE users
                SET current_streak = $1,
                    max_streak = $2,
                    last_streak_date = $3
                WHERE user_id = $4
            """, new_current, new_max, today, user_id)

        # Подтвердил в тот же день — ничего не меняем
        elif last_date == today:
            return

        # Пропустил — сброс
        else:
            await conn.execute("""
                UPDATE users
                SET current_streak = 1,
                    last_streak_date = $1
                WHERE user_id = $2
            """, today, user_id)

