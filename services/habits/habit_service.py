import aiosqlite
from config import DB_PATH
from utils.timezones import get_current_time

async def save_habit(
    user_id: int,
    name: str,
    days: int,
    description: str,
    is_challenge: bool = False,
    confirm_type: str = 'media'
):
    created_at = get_current_time()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO habits (user_id, name, days, description, done_days, is_challenge, confirm_type, created_at)
            VALUES (?, ?, ?, ?, 0, ?, ?, ?)
        """, (user_id, name, days, description, int(is_challenge), confirm_type, created_at))
        await db.commit()
