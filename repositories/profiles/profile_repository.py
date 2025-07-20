import aiosqlite
from config import DB_PATH
from utils.timezones import get_current_time

async def save_user(user_id: int, name: str | None = None):
    created_at = get_current_time()

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, name, created_at) VALUES (?, ?, ?)",
            (user_id, name or "—", created_at)
        )
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone()
