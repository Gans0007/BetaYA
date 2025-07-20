import aiosqlite
from datetime import datetime, timedelta
from config import DB_PATH
from models.habit import Habit 
from models.habit_model import Habit

async def get_habits_by_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT id, name, days, description, done_days, is_challenge, confirm_type
            FROM habits
            WHERE user_id = ?
        """, (user_id,))
        rows = await cursor.fetchall()
        await cursor.close()
        return rows


async def habit_exists(user_id: int, name: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM habits WHERE user_id = ? AND name = ?",
            (user_id, name)
        )
        result = await cursor.fetchone()
        await cursor.close()
        return result is not None



async def get_unconfirmed_today(user_id: int) -> list[Habit]:
    today = datetime.now().date().isoformat()
    habits: list[Habit] = []

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT *
            FROM habits h
            WHERE h.user_id = ?
              AND h.confirm_type != 'wake_time'
              AND h.done_days < h.days
              AND NOT EXISTS (
                  SELECT 1 FROM confirmations c
                  WHERE c.user_id = h.user_id AND c.habit_id = h.id AND DATE(c.datetime) = ?
              )
        """, (user_id, today))

        async for row in cursor:
            habits.append(Habit(*row))  # ✅ передаём все 10 полей

        await cursor.close()  # 💡 по желанию, но good practice

    return habits


async def get_progress_by_habit_id(habit_id: int) -> tuple[str, int, int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT name, done_days, days FROM habits WHERE id = ?",
            (habit_id,)
        )
        result = await cursor.fetchone()
        await cursor.close()

        if result:
            return result[0], result[1], result[2]  # name, done_days, total_days
        return "Без названия", 0, 0



async def increment_done_day(habit_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        # Увеличиваем выполненные дни
        await conn.execute(
            "UPDATE habits SET done_days = done_days + 1 WHERE id = ?",
            (habit_id,)
        )

        # Деактивируем привычку, если она завершена (и не из челенджа)
        await conn.execute("""
            UPDATE habits
            SET is_active = 0
            WHERE id = ?
              AND is_challenge = 0
              AND (SELECT done_days FROM habits WHERE id = ?) >= days
        """, (habit_id, habit_id))

        await conn.commit()



async def should_show_delete_button(user_id: int, habit_id: int) -> bool:
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    async with aiosqlite.connect(DB_PATH) as db:
        # Проверка подтверждений
        cursor = await db.execute("""
            SELECT DATE(datetime) FROM confirmations
            WHERE user_id = ? AND habit_id = ? AND confirmed = 1
        """, (user_id, habit_id))
        confirmed_rows = await cursor.fetchall()
        await cursor.close()

        confirmed_dates = {
            datetime.strptime(row[0], "%Y-%m-%d").date() for row in confirmed_rows
        }

        if confirmed_dates:
            return today not in confirmed_dates and yesterday not in confirmed_dates

        # Если подтверждений нет — проверка даты создания привычки
        cursor = await db.execute("""
            SELECT DATE(created_at) FROM habits WHERE id = ?
        """, (habit_id,))
        row = await cursor.fetchone()
        await cursor.close()

        if not row:
            return False

        created_date = datetime.strptime(row[0], "%Y-%m-%d").date()
        return (today - created_date).days >= 2



async def delete_habit_by_id(habit_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        await conn.execute("DELETE FROM confirmations WHERE habit_id = ?", (habit_id,))
        await conn.commit()


async def get_habit_by_id(habit_id: int) -> Habit | None:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        row = await cursor.fetchone()
        await cursor.close()  # ✅ Закрываем курсор

        if row:
            return Habit(*row)
        return None


async def complete_habit_by_id(habit_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        # Получаем user_id и done_days привычки
        async with conn.execute("SELECT user_id, done_days FROM habits WHERE id = ?", (habit_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return
            user_id, done_days = row

        # Удаляем привычку
        await conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))

        # Если привычка длилась 15+ дней — +1 в finished_habits
        if done_days >= 15:
            await conn.execute("""
                UPDATE users
                SET finished_habits = finished_habits + 1
                WHERE user_id = ?
            """, (user_id,))

        await conn.commit()



async def complete_and_remove_habit(habit: Habit):
    async with aiosqlite.connect(DB_PATH) as conn:
        if habit.done_days >= 15:
            await conn.execute("""
                INSERT INTO completed_habits (user_id, name, description, days, done_days, completed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                habit.user_id,
                habit.name,
                habit.description,
                habit.days,
                habit.done_days,
                datetime.now().isoformat()
            ))

        await conn.execute("DELETE FROM habits WHERE id = ?", (habit.id,))
        await conn.commit()


async def extend_habit_by_id(habit_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("UPDATE habits SET days = days + 5 WHERE id = ?", (habit_id,))
        await conn.commit()


async def count_user_habits(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM habits WHERE user_id = ?",
            (user_id,)
        )
        result = await cursor.fetchone()
        return result[0] if result else 0

