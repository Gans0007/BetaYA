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

async def get_confirmed_count(user_id: int) -> int:
    """
    Возвращает количество завершённых привычек у пользователя.
    Завершённая = done_days >= days
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT COUNT(*)
            FROM habits
            WHERE user_id = ? AND done_days >= days
        """, (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else 0

from config import DB_PATH
import aiosqlite

async def get_all_user_ids() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
