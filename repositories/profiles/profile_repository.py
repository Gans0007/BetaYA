from db.db import database
from utils.timezones import get_current_time

async def save_user(user_id: int, name: str | None = None):
    created_at = get_current_time()

    await database.execute("""
        INSERT INTO users (user_id, name, created_at)
        VALUES (:user_id, :name, :created_at)
        ON CONFLICT (user_id) DO NOTHING
    """, {
        "user_id": user_id,
        "name": name or "—",
        "created_at": created_at
    })


async def get_user(user_id: int):
    return await database.fetch_one("""
        SELECT * FROM users WHERE user_id = :user_id
    """, {"user_id": user_id})
