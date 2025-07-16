import aiosqlite
from datetime import datetime
from config import DB_PATH

async def save_habit(
    user_id: int,
    name: str,
    days: int,
    description: str,
    is_challenge: bool = False,
    confirm_type: str = 'media'
):
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO habits (user_id, name, days, description, done_days, is_challenge, confirm_type, created_at)
            VALUES (?, ?, ?, ?, 0, ?, ?, ?)
        """, (user_id, name, days, description, int(is_challenge), confirm_type, created_at))
        await db.commit()
