# repositories/habit_repository.py

from core.database import get_pool

# =====================================================
# 🔹 Репозиторий: добавление пользовательской привычки
#     Этот слой работает ТОЛЬКО с базой данных.
#     - выполняет SQL-запросы
#     - не содержит логики
#     - не использует Telegram или FSM
# =====================================================
async def insert_habit(user_id: int, name: str, desc: str, days: int, diff: int):
    """
    Добавляет пользовательскую привычку в таблицу habits.

    Аргументы:
        user_id (int): Владелец привычки
        name (str): Название привычки
        desc (str): Описание привычки
        days (int): На сколько дней берётся привычка
        diff (int): Уровень сложности (1–3)

    Логика:
        - репозиторий работает ТОЛЬКО с базой
        - никаких Telegram-объектов
        - никаких вычислений
        - никаких FSM
        - только SQL
    """

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO habits 
                (user_id, name, description, days, confirm_type, is_challenge, difficulty)
            VALUES 
                ($1, $2, $3, $4, 'media', FALSE, $5)
            """,
            user_id, name, desc, days, diff
        )


async def count_active_habits(user_id: int) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM habits
            WHERE user_id = $1
              AND is_active = TRUE
        """, user_id)
    return result or 0
