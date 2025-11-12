# services/user_service.py

# -------------------------------
# 🔗 Связка репозиториев для пересчёта дней
# -------------------------------
from repositories.confirmations_repository import count_unique_confirm_days
from repositories.user_repository import update_total_confirmed_days

# -------------------------------
# 🔁 Пересчёт и сохранение уникальных дней
# -------------------------------
async def recalculate_total_confirmed_days(user_id: int) -> int:
    """
    🔹 Считает уникальные дни из confirmations.
    🔹 Сохраняет итог в users.total_confirmed_days.
    🔹 Возвращает новое значение.
    """
    total = await count_unique_confirm_days(user_id)
    await update_total_confirmed_days(user_id, total)
    return total
