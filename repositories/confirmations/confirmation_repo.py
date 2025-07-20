# repositories/confirmations/confirmation_repo.py
import aiosqlite
from pathlib import Path
from utils.timezones import get_current_time
from repositories.referrals.referral_repo import mark_referral_active
from aiogram import Bot

import logging


DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "habits.db"

logger = logging.getLogger(__name__) 

import logging
from aiogram import Bot
from config import DB_PATH
import aiosqlite
from utils.timezones import get_current_time
from repositories.referrals.referral_repo import mark_referral_active

logger = logging.getLogger(__name__)

async def log_confirmation(user_id: int, habit_id: int, file_id: str, file_type: str, bot: Bot):
    now = get_current_time()
    today_str = now.date().isoformat()

    async with aiosqlite.connect(DB_PATH) as conn:
        # Получаем дату последнего подтверждения
        cursor = await conn.execute("""
            SELECT last_confirmation_date FROM users WHERE user_id = ?
        """, (user_id,))
        result = await cursor.fetchone()
        last_date = result[0] if result else None

        logger.info(f"[CONFIRMATION] last_date={last_date}, today_str={today_str} для user_id={user_id}")

        new_active_day = last_date != today_str

        # Обновляем active_days и last_confirmation_date
        if new_active_day:
            await conn.execute("""
                UPDATE users
                SET active_days = active_days + 1,
                    last_confirmation_date = ?
                WHERE user_id = ?
            """, (today_str, user_id))
            logger.info(f"[CONFIRMATION] ✅ Обновили активность пользователя {user_id}")

        # Вставляем подтверждение
        await conn.execute("""
            INSERT INTO confirmations (user_id, habit_id, datetime, file_id, file_type, confirmed)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (user_id, habit_id, now.isoformat(sep=' '), file_id, file_type))
        logger.info(f"[CONFIRMATION] ✅ Сохранили подтверждение habit_id={habit_id} для user_id={user_id}")

        # Проверяем достижение 3 активных дней
        if new_active_day:
            cursor = await conn.execute("""
                SELECT active_days FROM users WHERE user_id = ?
            """, (user_id,))
            active_days = (await cursor.fetchone())[0]
            logger.info(f"[CONFIRMATION] У пользователя {user_id} сейчас {active_days} active_days")

            if active_days == 3:
                changed = await mark_referral_active(user_id, conn)
                if changed:
                    # Получаем referrer_id
                    cursor = await conn.execute("""
                        SELECT referrer_id FROM referrals WHERE invited_id = ?
                    """, (user_id,))
                    row = await cursor.fetchone()
                    if row:
                        referrer_id = row[0]
                        try:
                            await bot.send_message(
                                referrer_id,
                                f"🥳 Ваш приглашённый пользователь @{user_id} стал активным! Поздравляем!"
                            )
                            logger.info(f"[REFERRAL] ✅ Уведомление отправлено пригласившему {referrer_id}")
                        except Exception as e:
                            logger.error(f"[REFERRAL] ❌ Ошибка при отправке уведомления {referrer_id}: {e}")

        await conn.commit()

async def was_confirmed_today(user_id: int, habit_id: int) -> bool:
    today = get_current_time().date().isoformat()
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("""
            SELECT 1 FROM confirmations
            WHERE user_id = ? AND habit_id = ? AND DATE(datetime) = ?
        """, (user_id, habit_id, today))
        result = await cursor.fetchone()
        return result is not None


async def update_confirmation_file(user_id: int, habit_id: int, file_id: str, file_type: str):
    now = get_current_time()
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("""
            UPDATE confirmations
            SET datetime = ?, file_id = ?, file_type = ?
            WHERE user_id = ? AND habit_id = ? AND DATE(datetime) = DATE(?)
        """, (now, file_id, file_type, user_id, habit_id, now))
        await conn.commit()
