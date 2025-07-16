import aiosqlite
from config import DB_PATH

async def save_user(user_id: int, name: str | None = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)",
            (user_id, name or "—")
        )
        await db.commit()
