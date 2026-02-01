# repositories/profile_settings_repository.py
from database import get_pool


async def get_user_settings(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
            SELECT
                notification_tone,
                share_confirmation_media,
                timezone
            FROM users
            WHERE user_id = $1
        """, user_id)



async def update_notification_tone(user_id: int, tone_code: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET notification_tone = $1
            WHERE user_id = $2
        """, tone_code, user_id)

async def toggle_share_media(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        current = await conn.fetchval("""
            SELECT share_confirmation_media
            FROM users
            WHERE user_id = $1
        """, user_id)

        new_value = not bool(current)
        await conn.execute("""
            UPDATE users SET share_confirmation_media = $1
            WHERE user_id = $2
        """, new_value, user_id)

        return new_value
