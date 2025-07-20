# repositories/referrals/referral_repo.py

import aiosqlite
from config import DB_PATH
from utils.timezones import get_current_time

import logging
logger = logging.getLogger(__name__)

async def save_referral(referrer_id: int, invited_id: int):
    if referrer_id == invited_id:
        logger.info(f"[REFERRAL] ❌ Пользователь {invited_id} попытался пригласить сам себя")
        return

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM referrals WHERE invited_id = ?", (invited_id,)
        )
        if await cursor.fetchone():
            logger.info(f"[REFERRAL] ⚠️ Пользователь {invited_id} уже есть в базе — не сохраняем повторно")
            return

        await db.execute(
            "INSERT INTO referrals (referrer_id, invited_id, created_at) VALUES (?, ?, ?)",
            (referrer_id, invited_id, get_current_time())
        )
        await db.commit()
        logger.info(f"[REFERRAL] ✅ Сохранена связь: {referrer_id} → {invited_id}")


async def mark_referral_active(invited_id: int, db: aiosqlite.Connection) -> bool:
    cursor = await db.execute("""
        UPDATE referrals SET is_active = 1 WHERE invited_id = ? AND is_active = 0
    """, (invited_id,))
    if cursor.rowcount > 0:
        logger.info(f"[REFERRAL] 🎯 Приглашённый {invited_id} стал активным рефералом")
        return True
    return False


async def get_referral_stats(referrer_id: int) -> tuple[int, int]:
    async with aiosqlite.connect(DB_PATH) as db:
        total_row = await db.execute_fetchone(
            "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (referrer_id,)
        )
        active_row = await db.execute_fetchone(
            "SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND is_active = 1", (referrer_id,)
        )
        return total_row[0] if total_row else 0, active_row[0] if active_row else 0
