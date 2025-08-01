from datetime import datetime, timedelta
import pytz
import logging
from repositories.habits.habit_repo import get_habit_by_id
from services.confirmations.confirmation_service import (
    process_confirmation,
    send_to_public_chat,
)
from services.challenge_service.complete_challenge import complete_challenge

logger = logging.getLogger(__name__)

KYIV_TZ = pytz.timezone("Europe/Kyiv")

async def check_wake_time(habit_name: str) -> tuple[bool, str | None]:
    """
    Проверка что текущее время в допустимом окне wake_time
    Возвращает (ok, error_text)
    """
    try:
        time_part = habit_name.split("в")[1].strip()
        wake_time = datetime.strptime(time_part, "%H:%M").time()
        now = datetime.now(KYIV_TZ).time()
        latest_allowed = (datetime.combine(datetime.today(), wake_time) + timedelta(minutes=4)).time()

        if not (wake_time <= now <= latest_allowed):
            return False, f"⏰ Подтверждение допускается только с {wake_time.strftime('%H:%M')} до {latest_allowed.strftime('%H:%M')}.\nСегодня уже поздно."
        return True, None
    except Exception:
        return False, "❌ Невозможно определить время подъема."


async def start_confirmation(user_id: int, habit_id: int):
    """
    Логика при нажатии кнопки 'Подтвердить'
    """
    habit = await get_habit_by_id(habit_id)
    if not habit:
        return None, "❌ Привычка не найдена."

    # если wake_time, проверяем окно
    if habit.confirm_type == "wake_time":
        ok, error = await check_wake_time(habit.name)
        if not ok:
            return None, error

    return habit, None


async def confirm_with_media(user, habit_id: int, file_id: str, file_type: str, bot):
    """
    Основная логика обработки присланного медиа.
    """
    habit = await get_habit_by_id(habit_id)
    if not habit:
        return "❌ Привычка не найдена."

    # Проверка времени для wake_time
    if habit.confirm_type == "wake_time":
        ok, error = await check_wake_time(habit.name)
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

    # Отправляем в паблик-чат
    await send_to_public_chat(
        user=user,
        habit_id=habit_id,
        file_id=file_id,
        file_type=file_type,
        bot=bot
    )

    # Проверка завершения челленджа
    if progress_increased:
        habit = await get_habit_by_id(habit_id)
        if habit.is_challenge and int(habit.done_days) >= int(habit.days):
            await complete_challenge(habit_id, user.id, bot)
            return "🏆 Челлендж завершён!"

    return "✅ Привычка успешно подтверждена! Прогресс обновлён." if progress_increased else "♻️ Медиа обновлено! Прогресс не изменён."
