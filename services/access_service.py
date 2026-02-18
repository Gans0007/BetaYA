# services/access_service.py

from datetime import datetime, timezone
from typing import Tuple
from core.database import get_pool
from repositories.user_repository import get_user_by_id
from repositories.habit_repository import count_active_habits

# ====== НАСТРОЙКИ ======
FREE_HABIT_LIMIT = 2
# =======================


async def can_add_habit(user_id: int) -> Tuple[bool, int]:

    pool = await get_pool()
    user = await get_user_by_id(pool, user_id)

    now = datetime.now(timezone.utc)

    # ✅ Проверяем только дату
    if (
        user
        and user["access_until"]
        and user["access_until"] > now
    ):
        return True, 0

    active_count = await count_active_habits(user_id)

    if active_count < FREE_HABIT_LIMIT:
        return True, active_count

    return False, active_count