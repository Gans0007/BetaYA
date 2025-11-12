# repositories/user_repository.py

from database import get_pool

# -------------------------------
# 🔁 Обновление общего количества подтверждённых дней
# -------------------------------
async def update_total_confirmed_days(user_id: int, total_days: int) -> None:
    """
    🔹 Обновляет поле total_confirmed_days в таблице users.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET total_confirmed_days = $1
            WHERE user_id = $2
        """, total_days, user_id)
