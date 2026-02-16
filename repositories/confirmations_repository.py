# repositories/confirmations_repository.py

from core.database import get_pool

# -------------------------------
# 📊 Подсчёт уникальных подтверждённых дней
# -------------------------------
async def count_unique_confirm_days(user_id: int) -> int:
    """
    🔹 Считает количество уникальных дат (DATE(datetime)) подтверждений.
    🔹 Берём только записи, где confirmed = TRUE.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        val = await conn.fetchval("""
            SELECT COUNT(DISTINCT DATE(datetime))
            FROM confirmations
            WHERE user_id = $1
              AND (confirmed = TRUE OR confirmed IS NULL)  -- если confirmed не всегда проставляешь
        """, user_id)
        return val or 0
