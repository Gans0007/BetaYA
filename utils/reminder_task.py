import logging
import asyncio
import random
from datetime import datetime, timedelta
from aiogram import Bot
from utils.reminder_storage import add_reminder, remove_reminder, get_reminder, cancel_all_reminders
from aiogram.exceptions import TelegramForbiddenError, TelegramNetworkError

from repositories.users.user_repo import get_all_users_with_active_habits
from repositories.habits.habit_repo import get_unconfirmed_today

logger = logging.getLogger(__name__)
MIN_HOUR, MAX_HOUR = 9, 20

async def schedule_reminder(bot: Bot, user_id: int, habit_id: int):
    """
    Планирует одноразовое напоминание для непродтверждённой привычки,
    если оно ещё не запланировано.
    """
    # Проверяем, не запланировано ли уже напоминание
    existing = get_reminder(user_id, habit_id)
    if existing:
        logger.debug(f"[REMINDER] Напоминание для habit={habit_id} user={user_id} уже запланировано")
        return

    now = datetime.now()
    target_hour = random.randint(MIN_HOUR, MAX_HOUR)
    target_minute = random.randint(0, 59)
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if target_time < now:
        target_time += timedelta(days=1)
    delay = (target_time - now).total_seconds()

    logger.info(f"[REMINDER] Для привычки {habit_id} (user={user_id}) — запланировано на {target_time}")
    task = asyncio.create_task(remind_once(bot, user_id, habit_id, delay))
    add_reminder(user_id, habit_id, task)



async def remind_once(bot: Bot, user_id: int, habit_id: int, delay: float):
    await asyncio.sleep(delay)

    try:
        habits = await get_unconfirmed_today(user_id)
        habit = next((h for h in habits if h.id == habit_id), None)
        if not habit:
            remove_reminder(user_id, habit_id)
            return

        text = (
            f"🔔 Напоминание: не забудь подтвердить «{habit.name}» "
            f"({habit.done_days} / {habit.days})\n\n"
            "⚠️ Если ты пропустишь день — счётчик аннулируется."
        )

        await bot.send_message(user_id, text)
        logger.info(f"[REMINDER] Отправлено пользователю {user_id} по привычке {habit_id}")

    except TelegramForbiddenError:
        logger.warning(f"[REMINDER] ❌ Пользователь {user_id} заблокировал бота.")
    except TelegramNetworkError as e:
        logger.warning(f"[REMINDER] 🌐 Сетевая ошибка при отправке пользователю {user_id}: {e}")
    except ConnectionError as e:
        logger.warning(f"[REMINDER] 🔌 Соединение разорвано при отправке пользователю {user_id}: {e}")
    except Exception as e:
        logger.exception(f"[REMINDER] Неизвестная ошибка при отправке пользователю {user_id}: {e}")
    finally:
        remove_reminder(user_id, habit_id)


async def send_reminders(bot: Bot):
    """
    Запускается APScheduler каждый час:
    планирует напоминания для всех непродтверждённых привычек
    """
    try:
        users = await get_all_users_with_active_habits()
        for user_id in users:
            habits = await get_unconfirmed_today(user_id)
            for habit in habits:
                await schedule_reminder(bot, user_id, habit.id)
    except Exception:
        logger.exception("Ошибка в send_reminders")

async def reset_all_reminders():
    """
    Отменяет все запланированные напоминания (например, при глобальном сбросе привычек).
    """
    cancel_all_reminders()
