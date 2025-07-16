from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from repositories.habits.habit_repo import get_habit_by_id
from repositories.confirmations.confirmation_repo import was_confirmed_today
from repositories.habits.habit_repo import should_show_delete_button

async def render_habit_card(message: Message, user_id: int, habit_id: int):
    habit = await get_habit_by_id(habit_id)
    if not habit:
        await message.edit_text("❌ Привычка не найдена.")
        return

    # Процент выполнения
    try:
        done_days = int(habit.done_days)
        days = int(habit.days)
        percent = round((done_days / days) * 100) if days > 0 else 0
    except (ZeroDivisionError, ValueError):
        percent = 0

    # Текст
    text = (
        f"⚡️Активная привычка:\n\n"
        f"<b>Название:</b> {habit.name}\n"
        f"<b>Описание:</b> {habit.description or '—'}\n"
        f"<b>Прогресс:</b> {habit.done_days} из {habit.days} дней  ({percent}%)"
    )

    # Кнопки
    buttons = []

    if not habit.is_challenge and done_days == days:
        # Завершена — показать Завершить/Продлить
        buttons.append(InlineKeyboardButton(text="🫠 Завершить", callback_data=f"complete_habit_{habit_id}"))
        buttons.append(InlineKeyboardButton(text="🫡 Продлить", callback_data=f"extend_habit_{habit_id}"))
    else:
        # Подтверждение
        if habit.confirm_type == "wake_time":
            confirm_text = "⏰ Подтвердить (до +4 мин)"
        elif await was_confirmed_today(user_id, habit_id):
            confirm_text = "♻️ Переподтвердить"
        else:
            confirm_text = "✅ Подтвердить"
        buttons.append(InlineKeyboardButton(text=confirm_text, callback_data=f"confirm_done_{habit_id}"))

        # Кнопка удаления
        if await should_show_delete_button(user_id, habit_id):
            buttons.append(InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_habit_{habit_id}"))

    # Показ
    markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
    await message.edit_text(text, reply_markup=markup, parse_mode="HTML")
