# repositories/profile_stats_repository.py
from core.database import get_pool


async def get_user_stats(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
            SELECT 
                u.username,
                u.nickname,

                COALESCE(s.finished_habits, 0) AS finished_habits,
                COALESCE(s.finished_challenges, 0) AS finished_challenges,
                COALESCE(s.total_stars, 0) AS total_stars,
                COALESCE(s.total_confirmed_days, 0) AS total_confirmed_days,
                u.joined_at,
                u.current_streak,
                u.max_streak,
                COALESCE(s.xp, 0) AS xp,
                u.league,
                u.league_emoji

            FROM users u
            LEFT JOIN user_stats s 
                ON s.user_id = u.user_id

            WHERE u.user_id = $1
        """, user_id)


async def update_league(user_id: int, league_name: str, league_emoji: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET league = $1,
                league_emoji = $2
            WHERE user_id = $3
        """, league_name, league_emoji, user_id)


async def get_last_confirmations_for_week(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("""
            SELECT COUNT(*) FROM confirmations
            WHERE user_id = $1 AND datetime > NOW() - INTERVAL '7 days'
        """, user_id)
