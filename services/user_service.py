# services/user_service.py
from datetime import date, timedelta
from core.database import get_pool

# -------------------------------
# 🔗 Связка репозиториев для пересчёта дней
# -------------------------------
from repositories.confirmations_repository import count_unique_confirm_days
from repositories.user_repository import update_total_confirmed_days
from services.user_stats_service import set_total_confirmed_days

# -------------------------------
# 🔁 Пересчёт и сохранение уникальных дней
# -------------------------------
async def recalculate_total_confirmed_days(conn, user_id: int) -> int:
    total = await count_unique_confirm_days(conn, user_id)
    await set_total_confirmed_days(conn, user_id, total)
    return total
