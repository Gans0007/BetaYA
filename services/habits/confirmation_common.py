from repositories.habits.habit_repo import get_habit_by_id
from services.confirmations.confirmation_service import process_confirmation, send_to_public_chat
from services.challenge_service.complete_challenge import complete_challenge

async def confirm_media_habit(user, habit_id: int, file_id: str, file_type: str, bot):
    """
    Общая логика подтверждения привычки через медиа.
    Используется и для кнопки, и для авто-подтверждения.
    """
    habit = await get_habit_by_id(habit_id)
    if not habit:
        return "❌ Привычка не найдена."

    # Проверка времени для wake_time
    if habit.confirm_type == "wake_time":
        from services.habits.habit_confirmation_service import check_wake_time
        ok, error = await check_wake_time(habit.name)
        if not ok:
            return error

    # Основная обработка
    progress_increased = await process_confirmation(
        user_id=user.id,
        habit_id=habit_id,
        file_id=file_id,
        file_type=file_type,
        bot=bot
    )

    # Отправляем в паблик-чат (асинхронно)
    await send_to_public_chat(
        user=user,
        habit_id=habit_id,
        file_id=file_id,
        file_type=file_type,
        bot=bot
    )

    # Проверяем завершение челленджа
    if progress_increased:
        habit = await get_habit_by_id(habit_id)

        # Ачивка за 3 подтверждения подряд
        from services.achievements.simple_achievements import show_achievement
        if habit.done_days == 3:
            await show_achievement(bot, user.id, "streak_3")

        # Проверка завершения челленджа
        if habit.is_challenge and int(habit.done_days) >= int(habit.days):
            await complete_challenge(habit_id, user.id, bot)
            return "🏆 Челлендж завершён!"

    return (
        "✅ Привычка успешно подтверждена! Прогресс обновлён."
        if progress_increased
        else "♻️ Медиа обновлено! Прогресс не изменён."
    )
