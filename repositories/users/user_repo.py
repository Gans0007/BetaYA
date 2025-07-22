# repositories/users/user_repo.py

from db.db import database

async def get_all_users_with_active_habits() -> list[int]:
    rows = await database.fetch_all("SELECT DISTINCT user_id FROM habits")
    return [row["user_id"] for row in rows]

async def get_confirmed_count(user_id: int) -> int:
    query = """
        SELECT COUNT(*) 
        FROM habits 
        WHERE user_id = :user_id AND done_days >= days
    """
    row = await database.fetch_one(query, {"user_id": user_id})
    return row[0] if row else 0

async def get_all_user_ids() -> list[int]:
    rows = await database.fetch_all("SELECT user_id FROM users")
    return [row["user_id"] for row in rows]
