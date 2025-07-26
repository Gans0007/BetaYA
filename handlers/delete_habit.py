import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.habits.delete_habit_service import (
    request_delete_confirmation,
    perform_delete,
    restore_habit_card
)

logger = logging.getLogger(__name__)
router = Router()

# Подтверждение удаления
@router.callback_query(F.data.startswith("delete_habit_"))
async def confirm_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    habit_id = int(callback.data.split("_")[-1])

    text, keyboard = await request_delete_confirmation(habit_id)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


# Удаление
@router.callback_query(F.data.startswith("confirm_delete_"))
async def delete_habit(callback: CallbackQuery):
    user_id = callback.from_user.id
    habit_id = int(callback.data.split("_")[-1])

    result_text = await perform_delete(habit_id)
    await callback.message.edit_text(result_text)
    await callback.answer()


# Отмена
@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    habit_id = int(callback.message.reply_markup.inline_keyboard[0][0].callback_data.split("_")[-1])

    reply_markup, text = await restore_habit_card(user_id, habit_id)
    if reply_markup is None:
        await callback.message.edit_text(text)
    else:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()
