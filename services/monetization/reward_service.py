# services/monetization/reward_service.py

import aiosqlite
from config import DB_PATH
from utils.timezones import get_current_time
import logging

logger = logging.getLogger(__name__)

async def add_reward(user_id: int, amount: float, reward_type: str, reason: str = "Без причины", conn: aiosqlite.Connection = None):
    if reward_type not in ["xp", "usdt"]:
        raise ValueError("Тип награды должен быть 'xp' или 'usdt'")

    internal_conn = False
    if conn is None:
        conn = await aiosqlite.connect(DB_PATH)
        internal_conn = True

    # Обновляем баланс
    if reward_type == "xp":
        await conn.execute("UPDATE users SET xp_balance = xp_balance + ? WHERE user_id = ?", (amount, user_id))
    else:
        await conn.execute("UPDATE users SET usdt_balance = usdt_balance + ? WHERE user_id = ?", (amount, user_id))

    # Пишем в историю
    await conn.execute("""
        INSERT INTO reward_history (user_id, amount, type, reason, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, amount, reward_type, reason, get_current_time()))

    if internal_conn:
        await conn.commit()
        await conn.close()

    logger.info(f"[REWARD] ✅ +{amount} {reward_type.upper()} → user_id={user_id}, причина: {reason}")
