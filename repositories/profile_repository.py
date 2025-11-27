from database import get_pool

async def get_is_affiliate(user_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("""
            SELECT is_affiliate
            FROM users
            WHERE user_id = $1
        """, user_id) or False
