# repositories/user_repository.py

from core.database import get_pool


# -------------------------------
# 🔁 Получить пользователя
# -------------------------------
async def get_user_by_id(pool, user_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
            SELECT *
            FROM users
            WHERE user_id = $1
        """, user_id)


# -------------------------------
# 🔁 Обновление общего количества подтверждённых дней
# -------------------------------
async def update_total_confirmed_days(user_id: int, total_days: int) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET total_confirmed_days = $1
            WHERE user_id = $2
        """, total_days, user_id)
