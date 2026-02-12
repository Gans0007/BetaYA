# services/access_service.py

from typing import Tuple
from database import get_pool
from repositories.user_repository import get_user_by_id
from repositories.habit_repository import count_active_habits

# ====== НАСТРОЙКИ ======
FREE_HABIT_LIMIT = 2
# =======================


async def can_add_habit(user_id: int) -> Tuple[bool, int]:
    """
    Проверяет, может ли пользователь добавить новую привычку.
    Возвращает:
        (True, count)  если можно
        (False, count) если нельзя
    """

    pool = await get_pool()
    user = await get_user_by_id(pool, user_id)

    # Если есть активная подписка → безлимит
    if user and user["has_access"]:
        return True, 0

    active_count = await count_active_habits(user_id)

    if active_count < FREE_HABIT_LIMIT:
        return True, active_count

    return False, active_count
