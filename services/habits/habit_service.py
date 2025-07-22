from db.db import database
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
    await database.execute("""
        INSERT INTO habits (user_id, name, days, description, done_days, is_challenge, confirm_type, created_at)
        VALUES (:user_id, :name, :days, :description, 0, :is_challenge, :confirm_type, :created_at)
    """, {
        "user_id": user_id,
        "name": name,
        "days": days,
        "description": description,
        "is_challenge": is_challenge,
        "confirm_type": confirm_type,
        "created_at": created_at
    })
