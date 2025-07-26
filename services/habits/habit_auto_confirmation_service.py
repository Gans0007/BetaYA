import logging
from datetime import datetime, timedelta
import pytz
from repositories.habits.habit_repo import get_habits_by_user, get_habit_by_id
from services.confirmations.confirmation_service import (
    process_confirmation,
    send_to_public_chat
)
from services.challenge_service.complete_challenge import complete_challenge

logger = logging.getLogger(__name__)
KYIV_TZ = pytz.timezone("Europe/Kyiv")


async def list_media_habits(user_id: int):
    """
    Возвращает список (habit_id, name) привычек пользователя,
    которые можно подтвердить через медиа
    """
    habits = await get_habits_by_user(user_id)
    return [(h.id, h.name) for h in habits if h.confirm_type in ("media", "wake_time")]


async def check_wake_time(habit) -> tuple[bool, str | None]:
    """
    Проверка, что текущее время допустимо для wake_time
    """
    try:
        name = habit.name
        time_part = name.split("в")[1].strip()
        wake_time = datetime.strptime(time_part, "%H:%M").time()
        now = datetime.now(KYIV_TZ).time()
        latest_allowed = (datetime.combine(datetime.today(), wake_time) + timedelta(minutes=4)).time()

        if not (wake_time <= now <= latest_allowed):
            return False, (
                f"⏰ Подтверждение допускается только с "
                f"{wake_time.strftime('%H:%M')} до {latest_allowed.strftime('%H:%M')}.\nСегодня уже поздно."
            )
        return True, None
    except Exception:
        return False, "❌ Невозможно определить время подъема."


async def confirm_selected_habit(user, habit_id: int, file_id: str, file_type: str, bot):
    """
    Основная логика авто-подтверждения через медиа.
    """
    habit = await get_habit_by_id(habit_id)
    if not habit:
        return "❌ Привычка не найдена."

    # Проверка времени
    if habit.confirm_type == "wake_time":
        ok, error = await check_wake_time(habit)
        if not ok:
            return error

    # Обработка подтверждения
    progress_increased = await process_confirmation(
        user_id=user.id,
        habit_id=habit_id,
        file_id=file_id,
        file_type=file_type,
        bot=bot
    )

    await send_to_public_chat(
        user=user,
        habit_id=habit_id,
        file_id=file_id,
        file_type=file_type,
        bot=bot
    )

    if progress_increased:
        habit = await get_habit_by_id(habit_id)
        if habit.is_challenge and int(habit.done_days) >= int(habit.days):
            await complete_challenge(habit_id, user.id, bot)
            return "🏆 Челлендж завершён!"

    return (
        "✅ Привычка успешно подтверждена! Прогресс обновлён."
        if progress_increased
        else "♻️ Видео/фото обновлено! Прогресс не изменён."
    )
