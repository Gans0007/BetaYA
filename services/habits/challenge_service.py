import logging
from repositories.habits.habit_repo import (
    get_habits_by_user,
    habit_exists,
    count_user_habits
)
from services.habits.habit_service import save_habit

logger = logging.getLogger(__name__)

MAX_HABITS = 3

async def can_add_challenge(user_id: int):
    """
    Проверяет, можно ли добавить новый челлендж.
    """
    total = await count_user_habits(user_id)
    return total < MAX_HABITS, total


async def add_new_challenge(user_id: int, title: str, desc: str, days: int, ctype: str):
    """
    Добавляет челлендж пользователю.
    """
    if await habit_exists(user_id, title):
        return False, "❌ Этот челлендж уже активен!"

    await save_habit(
        user_id=user_id,
        name=title,
        days=days,
        description=desc,
        is_challenge=True,
        confirm_type=ctype
    )

    habits = await get_habits_by_user(user_id)
    habit_id = habits[-1].id if habits else None

    logger.info(f"[{user_id}] Челлендж '{title}' добавлен (habit_id={habit_id})")
    return True, "✅ Челлендж добавлен в активные привычки!"
