# repositories/profile_stats_repository.py
from database import get_pool


async def get_user_stats(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
            SELECT username, nickname, finished_habits, finished_challenges,
                   total_stars, total_confirmed_days, joined_at,
                   current_streak, max_streak, xp,
                   league, league_emoji
            FROM users
            WHERE user_id = $1
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
