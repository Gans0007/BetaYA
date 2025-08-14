from aiogram import Bot
from utils.timezones import get_current_time
from services.monetization.reward_service import add_reward
from db.db import database
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def log_confirmation(user_id: int, habit_id: int, file_id: str, file_type: str, bot: Bot):
    now = get_current_time()
    today = now.date()

    # Получаем дату последнего подтверждения
    row = await database.fetch_one("""
        SELECT last_confirmation_date FROM users WHERE user_id = :user_id
    """, {"user_id": user_id})
    last_date = row["last_confirmation_date"] if row else None

    logger.info(f"[CONFIRMATION] last_date={last_date}, today={today} для user_id={user_id}")

    new_active_day = last_date != today

    if new_active_day:
        await database.execute("""
            UPDATE users
            SET active_days = active_days + 1,
                last_confirmation_date = :today
            WHERE user_id = :user_id
         """, {"today": today, "user_id": user_id}) 
        logger.info(f"[CONFIRMATION] ✅ Обновили активность пользователя {user_id}")

        # ✅ XP
        await add_reward(user_id, 2, "xp", "Первое подтверждение дня")

        try:
            await bot.send_message(user_id, "⭐ +2 XP за первое подтверждение дня!")
        except Exception as e:
            logger.error(f"[XP] ❌ Ошибка при отправке уведомления XP user_id={user_id}: {e}")

    # Вставляем подтверждение
    await database.execute("""
        INSERT INTO confirmations (user_id, habit_id, datetime, file_id, file_type, confirmed)
        VALUES (:user_id, :habit_id, :datetime, :file_id, :file_type, :confirmed)
    """, {
        "user_id": user_id,
        "habit_id": habit_id,
        "datetime": now,
        "file_id": file_id,
        "file_type": file_type,
        "confirmed": True  
    })
    logger.info(f"[CONFIRMATION] ✅ Сохранили подтверждение habit_id={habit_id} для user_id={user_id}")


async def was_confirmed_today(user_id: int, habit_id: int) -> bool:
    today = get_current_time().date()
    row = await database.fetch_one("""
        SELECT 1 FROM confirmations
        WHERE user_id = :user_id AND habit_id = :habit_id AND DATE(datetime) = :today
    """, {"user_id": user_id, "habit_id": habit_id, "today": today})
    return row is not None


async def update_confirmation_file(user_id: int, habit_id: int, file_id: str, file_type: str):
    now = get_current_time()
    await database.execute("""
        UPDATE confirmations
        SET datetime = :now, file_id = :file_id, file_type = :file_type
        WHERE user_id = :user_id AND habit_id = :habit_id AND DATE(datetime) = DATE(:now)
    """, {
        "now": now,
        "file_id": file_id,
        "file_type": file_type,
        "user_id": user_id,
        "habit_id": habit_id
    })
