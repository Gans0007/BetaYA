from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
import logging

from services.habits.habit_auto_confirmation_service import (
    list_media_habits,
    confirm_selected_habit,
)

logger = logging.getLogger(__name__)
router = Router()

# 🔹 Обработка медиа без состояния
@router.message(F.photo | F.video | F.video_note)
async def handle_media_no_state(message: Message, state: FSMContext):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    # Определяем тип медиа
    if message.photo:
        file_id, file_type = message.photo[-1].file_id, "photo"
    elif message.video:
        file_id, file_type = message.video.file_id, "video"
    elif message.video_note:
        file_id, file_type = message.video_note.file_id, "video_note"
    else:
        await message.answer("❌ Тип медиа не распознан.")
        return

    await state.update_data(file_id=file_id, file_type=file_type)

    try:
        media_habits = await list_media_habits(user_id)
        if not media_habits:
            await message.answer("😐 У тебя нет привычек, которые можно подтвердить через медиа.")
            return

        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=name, callback_data=f"select_habit_{hid}")]
                for hid, name in media_habits
            ]
        )

        await message.answer("Выбери, для какой привычки это подтверждение:", reply_markup=keyboard)
    except Exception as e:
        logger.exception(f"[{user_id}] Ошибка при обработке медиа: {e}")
        await message.answer("Произошла ошибка при обработке медиа.")
        await state.clear()


@router.callback_query(F.data.startswith("select_habit_"))
async def handle_habit_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    file_id = data.get("file_id")
    file_type = data.get("file_type")

    if not file_id or not file_type:
        await callback.message.answer("❌ Ошибка: медиа не найдено. Попробуй отправить снова.")
        await state.clear()
        return

    habit_id = int(callback.data.split("_")[-1])

    result_text = await confirm_selected_habit(
        user=callback.from_user,
        habit_id=habit_id,
        file_id=file_id,
        file_type=file_type,
        bot=callback.bot,
    )

    await callback.message.answer(result_text)
    await callback.answer()
    await state.clear()
