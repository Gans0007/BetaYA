import asyncio
import random
from datetime import timedelta
from utils.timezones import get_current_time
from repositories.habits.habit_repo import get_unconfirmed_today
from repositories.users.user_repo import get_all_user_ids
from aiogram import Bot
import random

MIN_HOUR = 8
MAX_HOUR = 21

import logging
logger = logging.getLogger(__name__)

async def scheduled_reminder_loop(bot: Bot):
    first_run = True

    while True:
        now = get_current_time()

        # 🕐 Первый запуск — через минуту после старта
        if first_run or (now.hour == 8 and now.minute == 0):
            first_run = False  # отключаем флаг первого запуска
            print(f"🚀 [REMINDER] Планируем напоминания на {now.date()}")

            user_ids = await get_all_user_ids()
            for user_id in user_ids:
                habits = await get_unconfirmed_today(user_id)
                for habit in habits:
                    # Рандомное время отправки (в пределах дня)
                    rand_hour = random.randint(MIN_HOUR, MAX_HOUR)
                    rand_min = random.randint(0, 59)
                    send_time = now.replace(hour=rand_hour, minute=rand_min, second=0, microsecond=0)

                    if send_time <= now:
                        send_time += timedelta(days=1)

                    delay = (send_time - now).total_seconds()
                    logger.info(f"[REMINDER] 🧠 habit_id={habit.id}, user_id={user_id} планируется на {send_time.strftime('%H:%M')}")
                    asyncio.create_task(send_delayed_reminder(bot, user_id, habit, delay))

        await asyncio.sleep(60)

async def send_delayed_reminder(bot: Bot, user_id: int, habit, delay: float):
    await asyncio.sleep(delay)

    # Повторно проверим, не подтвердил ли уже
    updated = await get_unconfirmed_today(user_id)
    if not any(h.id == habit.id for h in updated):
        return  # уже подтверждена, ничего не слать

    # ✅ Рандомные фразы в стиле Создателя
    phrases = [
        "⚠️ Не ленись, родной(ая)! \n\nГде дисциплина — там и прогресс. Подтверди: «{name}» ({done}/{total})",
        "⚠️ Не ленись, родной(ая)! \n\nБрат, победа не ждёт. Время: «{name}» ({done}/{total})",
        "⚠️ Не ленись, родной(ая)! \n\nТы выбрал путь сильных. Заверши: «{name}» ({done}/{total})",
        "⚠️ Не ленись, родной(ая)! \n\nПривычка формирует характер: «{name}» ({done}/{total})",
        "⚠️ Не ленись, родной(ая)! \n\nТы строишь себя. Подтверди привычку: «{name}» ({done}/{total})",
        "⚠️ Не ленись, родной(ая)! \n\nСильные не ищут оправданий. Сделай: «{name}» ({done}/{total})",
        "⚠️ Не ленись, родной(ая)! \n\nКаждый день решает. Сегодня ты победишь себя! «{name}» ({done}/{total})",
        "⚠️ Не ленись, родной(ая)! \n\nРодничек, у тебя есть ещё неподтверждённая привычка: «{name}» ({done}/{total})",
        "⚠️ Не ленись, родной(ая)! \n\nЦель близко. Поднимай жопу, пора: «{name}» ({done}/{total})",
        "⚠️ Не ленись, родной(ая)! \n\nПодтверди, что ты в игре. Есть неподтверждённая привычка: «{name}» ({done}/{total})"
    ]

    text = random.choice(phrases).format(
        name=habit.name,
        done=habit.done_days,
        total=habit.days
    )

    try:
        await bot.send_message(user_id, text)
    except Exception as e:
        print(f"[!] Ошибка при отправке пользователю {user_id} ({habit.name}): {e}")
