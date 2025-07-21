# repositories/referrals/referral_repo.py

import aiosqlite
from config import DB_PATH
from utils.timezones import get_current_time
from services.monetization.reward_service import add_reward

import logging
logger = logging.getLogger(__name__)

from aiogram import Bot

async def save_referral(referrer_id: int, invited_id: int, bot: Bot):
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

        await add_reward(referrer_id, 2, "xp", "Приглашён друг по ссылке", conn=db)
        await db.commit()

        logger.info(f"[REFERRAL] ✅ Сохранена связь: {referrer_id} → {invited_id}")

        try:
            await bot.send_message(
                referrer_id,
                "⭐ +2 XP в твою копилку 🧠"
            )
        except Exception as e:
            logger.warning(f"[REFERRAL] ❌ Не удалось отправить сообщение пользователю {referrer_id}: {e}")



async def get_referral_stats(referrer_id: int) -> tuple[int, int]:
    async with aiosqlite.connect(DB_PATH) as db:
        total_row = await db.execute_fetchone(
            "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (referrer_id,)
        )
        active_row = await db.execute_fetchone(
            "SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND is_active = 1", (referrer_id,)
        )
        return total_row[0] if total_row else 0, active_row[0] if active_row else 0
