# services/users/xp_service.py

import aiosqlite
from config import DB_PATH
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def add_xp(user_id: int, amount: int, reason: str = "Без причины", conn: aiosqlite.Connection = None):
    internal_conn = False

    if conn is None:
        conn = await aiosqlite.connect(DB_PATH)
        internal_conn = True

    await conn.execute("""
        UPDATE users
        SET xp_balance = xp_balance + ?
        WHERE user_id = ?
    """, (amount, user_id))

    await conn.execute("""
        INSERT INTO reward_history (user_id, amount, type, reason, timestamp)
        VALUES (?, ?, 'xp', ?, ?)
    """, (user_id, amount, reason, datetime.now().isoformat(sep=' ')))

    if internal_conn:
        await conn.commit()
        await conn.close()

    logger.info(f"[XP] ✅ +{amount} XP → user_id={user_id}, причина: {reason}")
