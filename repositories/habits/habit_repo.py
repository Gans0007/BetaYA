from datetime import datetime, timedelta
from models.habit_model import Habit
from db.db import database
from utils.timezones import get_current_time


async def get_habits_by_user(user_id: int):
    rows = await database.fetch_all("""
        SELECT id, user_id, name, days, description, done_days, is_active,
               is_challenge, confirm_type, created_at
        FROM habits
        WHERE user_id = :user_id
    """, {"user_id": user_id})
    return [Habit(**row) for row in rows]


async def habit_exists(user_id: int, name: str) -> bool:
    result = await database.fetch_one("""
        SELECT 1 FROM habits WHERE user_id = :user_id AND name = :name
    """, {"user_id": user_id, "name": name})
    return result is not None


async def get_unconfirmed_today(user_id: int) -> list[Habit]:
    today = get_current_time().date()
    rows = await database.fetch_all("""
        SELECT h.* FROM habits h
        WHERE h.user_id = :user_id
          AND h.confirm_type != 'wake_time'
          AND h.done_days < h.days
          AND NOT EXISTS (
              SELECT 1 FROM confirmations c
              WHERE c.user_id = h.user_id AND c.habit_id = h.id AND DATE(c.datetime) = :today
          )
    """, {"user_id": user_id, "today": today})
    return [Habit(**row) for row in rows]


async def get_progress_by_habit_id(habit_id: int):
    result = await database.fetch_one("""
        SELECT name, done_days, days FROM habits WHERE id = :habit_id
    """, {"habit_id": habit_id})
    return result if result else ("Без названия", 0, 0)


async def increment_done_day(habit_id: int):
    await database.execute("""
        UPDATE habits SET done_days = done_days + 1 WHERE id = :habit_id
    """, {"habit_id": habit_id})

    await database.execute("""
        UPDATE habits
        SET is_active = FALSE
        WHERE id = :habit_id
          AND is_challenge = FALSE
          AND (SELECT done_days FROM habits WHERE id = :habit_id) >= days
    """, {"habit_id": habit_id})


async def should_show_delete_button(user_id: int, habit_id: int) -> bool:
    today = get_current_time().date()
    yesterday = today - timedelta(days=1)

    confirmed = await database.fetch_all("""
        SELECT DATE(datetime) as date FROM confirmations
        WHERE user_id = :user_id AND habit_id = :habit_id AND confirmed = TRUE
    """, {"user_id": user_id, "habit_id": habit_id})

    confirmed_dates = {row["date"] for row in confirmed}

    if confirmed_dates:
        return today not in confirmed_dates and yesterday not in confirmed_dates

    created = await database.fetch_one("""
        SELECT DATE(created_at) as created FROM habits WHERE id = :habit_id
    """, {"habit_id": habit_id})

    if not created:
        return False

    created_date = created["created"]
    return (today - created_date).days >= 2


async def delete_habit_by_id(habit_id: int):
    await database.execute("DELETE FROM habits WHERE id = :id", {"id": habit_id})
    await database.execute("DELETE FROM confirmations WHERE habit_id = :id", {"id": habit_id})


async def get_habit_by_id(habit_id: int) -> Habit | None:
    row = await database.fetch_one("SELECT * FROM habits WHERE id = :id", {"id": habit_id})
    return Habit(**row) if row else None


async def complete_habit_by_id(habit_id: int):
    result = await database.fetch_one("SELECT user_id, done_days FROM habits WHERE id = :id", {"id": habit_id})
    if not result:
        return

    user_id, done_days = result["user_id"], result["done_days"]
    await database.execute("DELETE FROM habits WHERE id = :id", {"id": habit_id})

    if done_days >= 15:
        await database.execute("""
            UPDATE users SET finished_habits = finished_habits + 1 WHERE user_id = :user_id
        """, {"user_id": user_id})


async def complete_and_remove_habit(habit: Habit):
    if habit.done_days >= 15:
        await database.execute("""
            INSERT INTO completed_habits (user_id, name, description, days, done_days, completed_at)
            VALUES (:user_id, :name, :description, :days, :done_days, :completed_at)
        """, {
            "user_id": habit.user_id,
            "name": habit.name,
            "description": habit.description,
            "days": habit.days,
            "done_days": habit.done_days,
            "completed_at": datetime.now().isoformat()
        })

    await database.execute("DELETE FROM habits WHERE id = :id", {"id": habit.id})


async def extend_habit_by_id(habit_id: int):
    await database.execute("""
        UPDATE habits SET days = days + 5, is_active = TRUE WHERE id = :id
    """, {"id": habit_id})


async def count_user_habits(user_id: int) -> int:
    result = await database.fetch_one("SELECT COUNT(*) as count FROM habits WHERE user_id = :user_id", {"user_id": user_id})
    return result["count"] if result else 0
