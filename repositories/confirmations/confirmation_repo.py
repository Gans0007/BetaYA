# repositories/confirmations/confirmation_repo.py
import aiosqlite
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "habits.db"


async def log_confirmation(user_id: int, habit_id: int, file_id: str, file_type: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("""
            INSERT INTO confirmations (user_id, habit_id, datetime, file_id, file_type, confirmed)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (user_id, habit_id, now, file_id, file_type))
        await conn.commit()


async def was_confirmed_today(user_id: int, habit_id: int) -> bool:
    today = datetime.now().date().isoformat()
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("""
            SELECT 1 FROM confirmations
            WHERE user_id = ? AND habit_id = ? AND DATE(datetime) = ?
        """, (user_id, habit_id, today))
        result = await cursor.fetchone()
        return result is not None


async def update_confirmation_file(user_id: int, habit_id: int, file_id: str, file_type: str):
    now = datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("""
            UPDATE confirmations
            SET datetime = ?, file_id = ?, file_type = ?
            WHERE user_id = ? AND habit_id = ? AND DATE(datetime) = DATE(?)
        """, (now, file_id, file_type, user_id, habit_id, now))
        await conn.commit()


