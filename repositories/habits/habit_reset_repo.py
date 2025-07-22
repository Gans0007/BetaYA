from datetime import datetime
from db.db import database

async def reset_unconfirmed_habits(user_id: int):
    today = datetime.now().date()
    dropped = []

    # Получаем привычки пользователя (не челенджи)
    habits = await database.fetch_all("""
        SELECT id, name FROM habits
        WHERE user_id = :user_id
          AND confirm_type != 'wake_time'
          AND is_active = TRUE
          AND is_challenge = FALSE
    """, {"user_id": user_id})

    for habit in habits:
        # Проверка: была ли подтверждена сегодня
        confirmed = await database.fetch_one("""
            SELECT 1 FROM confirmations
            WHERE user_id = :user_id
              AND habit_id = :habit_id
              AND DATE(datetime) = :today
        """, {"user_id": user_id, "habit_id": habit.id, "today": today})

        if confirmed is None:
            await database.execute("""
                UPDATE habits SET done_days = 0 WHERE id = :habit_id
            """, {"habit_id": habit.id})
            dropped.append(habit.name)

    return dropped


async def reset_unconfirmed_challenges(user_id: int):
    today = datetime.now().date()
    dropped = []

    # Получаем только активные челленджи
    challenges = await database.fetch_all("""
        SELECT id, name FROM habits
        WHERE user_id = :user_id
          AND is_active = TRUE
          AND is_challenge = TRUE
    """, {"user_id": user_id})

    for challenge in challenges:
        confirmed = await database.fetch_one("""
            SELECT 1 FROM confirmations
            WHERE user_id = :user_id
              AND habit_id = :habit_id
              AND DATE(datetime) = :today
        """, {"user_id": user_id, "habit_id": challenge.id, "today": today})

        if confirmed is None:
            await database.execute("""
                UPDATE habits SET done_days = 0 WHERE id = :habit_id
            """, {"habit_id": challenge.id})
            dropped.append(challenge.name)

    return dropped
