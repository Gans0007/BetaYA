# ================================
#  honor_global_service.py
# ================================

from database import get_pool


async def get_global_rank(user_id: int) -> int | None:
    """
    Возвращает место пользователя в общем глобальном рейтинге по XP.
    1 = лучший
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        users = await conn.fetch("""
            SELECT user_id, xp
            FROM users
            ORDER BY xp DESC
        """)

    for idx, row in enumerate(users, start=1):
        if row["user_id"] == user_id:
            return idx

    return None
