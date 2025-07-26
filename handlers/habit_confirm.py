from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from states.habit_states import ConfirmHabit
import logging

from services.habits.habit_confirmation_service import start_confirmation, confirm_with_media

logger = logging.getLogger(__name__)
router = Router()

cancel_keyboard = types.InlineKeyboardMarkup(
    inline_keyboard=[[types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm_confirmation")]]
)

@router.callback_query(F.data.startswith("confirm_done_"))
async def handle_confirm_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    habit_id = int(callback.data.split("_")[-1])
    habit, error = await start_confirmation(user_id, habit_id)

    if error:
        await callback.message.answer(error)
        await callback.answer()
        return

    await state.update_data(habit_id=habit_id, confirm_type=habit.confirm_type)
    await callback.message.answer(
        f"📹 Пришли кружок или видео для подтверждения привычки: {habit.name}",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ConfirmHabit.waiting_for_media)
    await callback.answer()


@router.message(ConfirmHabit.waiting_for_media, F.video | F.video_note | F.photo)
async def handle_habit_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    habit_id = data.get("habit_id")

    if habit_id is None:
        await message.answer("❌ Произошла ошибка. Попробуй снова.")
        return

    # Определяем тип файла
    if message.video:
        file_id, file_type = message.video.file_id, "video"
    elif message.video_note:
        file_id, file_type = message.video_note.file_id, "video_note"
    else:
        file_id, file_type = message.photo[-1].file_id, "photo"

    result_text = await confirm_with_media(
        user=message.from_user,
        habit_id=habit_id,
        file_id=file_id,
        file_type=file_type,
        bot=message.bot
    )

    await message.answer(result_text)
    await state.clear()


@router.callback_query(F.data == "cancel_fsm_confirmation")
async def cancel_fsm_confirmation(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🚫 Подтверждение привычки отменено.")
    await callback.answer()
