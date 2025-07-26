import logging
from repositories.habits.habit_repo import (
    delete_habit_by_id,
    get_habit_by_id,
    should_show_delete_button,
)
from services.confirmations.confirmation_service import was_confirmed_today
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

async def request_delete_confirmation(habit_id: int):
    """
    Возвращает клавиатуру для подтверждения удаления.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Подтвердить удаление", callback_data=f"confirm_delete_{habit_id}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_delete")
    ]])
    return "⚠️ Ты точно хочешь удалить эту привычку?", keyboard


async def perform_delete(habit_id: int):
    """
    Удаляет привычку.
    """
    await delete_habit_by_id(habit_id)
    return "✅ Привычка удалена."


async def restore_habit_card(user_id: int, habit_id: int):
    """
    Возвращает текст и клавиатуру карточки привычки после отмены удаления.
    """
    habit = await get_habit_by_id(habit_id)
    if not habit:
        return None, "❌ Привычка не найдена."

    percent = round((habit.done_days / habit.days) * 100) if habit.days > 0 else 0
    title = "🔥<b>Активный челлендж:</b>" if habit.is_challenge else "⚡️<b>Активная привычка:</b>"

    text = (
        f"{title}\n\n"
        f"<b>Название:</b> {habit.name}\n"
        f"<b>Описание:</b> {habit.description}\n"
        f"<b>Прогресс:</b> {habit.done_days} из {habit.days} дней  <b>( {percent}% ) </b>"
    )

    # Кнопки
    buttons = [
        InlineKeyboardButton(
            text="♻️ Переподтвердить" if await was_confirmed_today(user_id, habit_id) else "✅ Подтвердить",
            callback_data=f"confirm_done_{habit_id}"
        )
    ]

    if await should_show_delete_button(user_id, habit_id):
        buttons.append(
            InlineKeyboardButton(
                text="🗑 Удалить",
                callback_data=f"delete_habit_{habit_id}"
            )
        )

    reply_markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return reply_markup, text
