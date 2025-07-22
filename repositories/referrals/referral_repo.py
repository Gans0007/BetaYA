# repositories/referrals/referral_repo.py

from aiogram import Bot
from db.db import database
from utils.timezones import get_current_time
from services.monetization.reward_service import add_reward

import logging
logger = logging.getLogger(__name__)

async def save_referral(referrer_id: int, invited_id: int, bot: Bot):
    if referrer_id == invited_id:
        logger.info(f"[REFERRAL] ❌ Пользователь {invited_id} попытался пригласить сам себя")
        return

    existing = await database.fetch_one(
        "SELECT 1 FROM referrals WHERE invited_id = :invited_id",
        {"invited_id": invited_id}
    )
    if existing:
        logger.info(f"[REFERRAL] ⚠️ Пользователь {invited_id} уже есть в базе — не сохраняем повторно")
        return

    query = """
        INSERT INTO referrals (referrer_id, invited_id, created_at)
        VALUES (:referrer_id, :invited_id, :created_at)
    """
    values = {
        "referrer_id": referrer_id,
        "invited_id": invited_id,
        "created_at": get_current_time()
    }
    await database.execute(query=query, values=values)

    # XP-награда за приглашение
    await add_reward(referrer_id, 2, "xp", "Приглашён друг по ссылке")

    logger.info(f"[REFERRAL] ✅ Сохранена связь: {referrer_id} → {invited_id}")

    try:
        await bot.send_message(referrer_id, "⭐ +2 XP в твою копилку 🧠")
    except Exception as e:
        logger.warning(f"[REFERRAL] ❌ Не удалось отправить сообщение пользователю {referrer_id}: {e}")


async def get_referral_stats(referrer_id: int) -> tuple[int, int]:
    total_row = await database.fetch_one(
        "SELECT COUNT(*) as count FROM referrals WHERE referrer_id = :referrer_id",
        {"referrer_id": referrer_id}
    )
    active_row = await database.fetch_one(
        "SELECT COUNT(*) as count FROM referrals WHERE referrer_id = :referrer_id AND is_active = TRUE",
        {"referrer_id": referrer_id}
    )
    return total_row["count"] if total_row else 0, active_row["count"] if active_row else 0
