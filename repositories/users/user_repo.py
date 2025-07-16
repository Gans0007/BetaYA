# repositories/users/user_repo.py

import aiosqlite
from config import DB_PATH

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("SELECT DISTINCT user_id FROM habits")
        rows = await cursor.fetchall()
        await cursor.close()
        return [row[0] for row in rows]


async def get_all_users_with_active_habits() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT DISTINCT user_id FROM habits") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]