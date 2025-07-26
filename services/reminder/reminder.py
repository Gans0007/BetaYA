import asyncio
import random
import logging
from datetime import timedelta
from aiogram import Bot
from utils.timezones import get_current_time
from repositories.habits.habit_repo import get_unconfirmed_today
from repositories.users.user_repo import get_all_user_ids

logger = logging.getLogger(__name__)

MIN_HOUR = 8
MAX_HOUR = 21

async def scheduled_reminder_loop(bot: Bot):
    """
    Бесконечный цикл, который раз в минуту проверяет,
    нужно ли распланировать напоминания на сегодня.
    """
    already_planned = False  # чтобы не планировать много раз в день

    while True:
        try:
            now = get_current_time()

            # Если ещё не планировали на сегодня — планируем
            if not already_planned or (now.hour == 8 and now.minute == 0):
                logger.info(f"[REMINDER] Планируем напоминания на {now.date()}")
                await plan_reminders_for_today(bot, now)
                already_planned = True

            await asyncio.sleep(60)

        except Exception as e:
            logger.exception(f"[REMINDER] Ошибка в scheduled_reminder_loop: {e}")
            await asyncio.sleep(10)  # чтобы не упасть навсегда


async def plan_reminders_for_today(bot: Bot, now):
    """
    Планирует отложенные задачи для всех привычек на сегодня.
    """
    user_ids = await get_all_user_ids()
    for user_id in user_ids:
        habits = await get_unconfirmed_today(user_id)
        for habit in habits:
            # Рандомное время отправки
            rand_hour = random.randint(MIN_HOUR, MAX_HOUR)
            rand_min = random.randint(0, 59)
            send_time = now.replace(hour=rand_hour, minute=rand_min, second=0, microsecond=0)
            if send_time <= now:
                send_time += timedelta(days=1)

            delay = (send_time - now).total_seconds()
            logger.info(f"[REMINDER] habit_id={habit.id}, user_id={user_id} на {send_time.strftime('%H:%M')}")
            asyncio.create_task(send_delayed_reminder(bot, user_id, habit, delay))


async def send_delayed_reminder(bot: Bot, user_id: int, habit, delay: float):
    """
    Отправляет напоминание после задержки, если привычка всё ещё не подтверждена.
    """
    try:
        await asyncio.sleep(delay)

        updated = await get_unconfirmed_today(user_id)
        if not any(h.id == habit.id for h in updated):
            return  # уже подтверждена

        text = random.choice([
            "⚠️ Не ленись, родной(ая)! \n\nГде дисциплина — там и прогресс. Подтверди: «{name}» ({done}/{total})",
            "⚠️ Брат, победа не ждёт. Время: «{name}» ({done}/{total})",
            "⚠️ Ты выбрал путь сильных. Заверши: «{name}» ({done}/{total})",
            "⚠️ Привычка формирует характер: «{name}» ({done}/{total})",
            "⚠️ Ты строишь себя. Подтверди: «{name}» ({done}/{total})",
            "⚠️ Сильные не ищут оправданий. Сделай: «{name}» ({done}/{total})",
            "⚠️ Каждый день решает. Сегодня ты победишь себя! «{name}» ({done}/{total})",
            "⚠️ Родничек, у тебя есть ещё неподтверждённая привычка: «{name}» ({done}/{total})",
            "⚠️ Цель близко. Поднимай жопу, пора: «{name}» ({done}/{total})",
            "⚠️ Подтверди, что ты в игре. Есть неподтверждённая привычка: «{name}» ({done}/{total})"
        ]).format(name=habit.name, done=habit.done_days, total=habit.days)

        await bot.send_message(user_id, text)

    except Exception as e:
        logger.exception(f"[REMINDER] Ошибка при отправке пользователю {user_id}: {e}")
