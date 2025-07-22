from db.db import database
from utils.timezones import get_current_time
import logging

logger = logging.getLogger(__name__)

async def add_reward(user_id: int, amount: float, reward_type: str, reason: str = "Без причины"):
    if reward_type not in ["xp", "usdt"]:
        logger.error(f"[REWARD] ❌ Некорректный тип награды: {reward_type} → user_id={user_id}")
        raise ValueError("Тип награды должен быть 'xp' или 'usdt'")

    try:
        if reward_type == "xp":
            result = await database.execute("""
                UPDATE users SET xp_balance = xp_balance + :amount WHERE user_id = :user_id
            """, {"amount": amount, "user_id": user_id})
        else:
            result = await database.execute("""
                UPDATE users SET usdt_balance = usdt_balance + :amount WHERE user_id = :user_id
            """, {"amount": amount, "user_id": user_id})

        if result == 0:
            logger.warning(f"[REWARD] ⚠️ Не удалось обновить баланс: user_id={user_id} не найден")

        await database.execute("""
            INSERT INTO reward_history (user_id, amount, type, reason, timestamp)
            VALUES (:user_id, :amount, :type, :reason, :timestamp)
        """, {
            "user_id": user_id,
            "amount": amount,
            "type": reward_type,
            "reason": reason,
            "timestamp": get_current_time()
        })

        logger.info(f"[REWARD] ✅ Начислено +{amount} {reward_type.upper()} → user_id={user_id}, причина: {reason}")

    except Exception as e:
        logger.exception(f"[REWARD] ❌ Ошибка при начислении награды: {e}")
