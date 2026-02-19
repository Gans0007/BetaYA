# ================================
#  honor_global_service.py
# ================================

from core.database import get_pool


async def get_global_rank(user_id: int) -> int | None:
    """
    Возвращает место пользователя в общем глобальном рейтинге по XP.
    1 = лучший
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        users = await conn.fetch("""
            SELECT u.user_id, COALESCE(s.xp, 0) AS xp
            FROM users u
            LEFT JOIN user_stats s ON s.user_id = u.user_id
            ORDER BY xp DESC
        """)

    for idx, row in enumerate(users, start=1):
        if row["user_id"] == user_id:
            return idx

    return None

