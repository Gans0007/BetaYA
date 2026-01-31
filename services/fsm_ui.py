# services/fsm_ui.py

from aiogram.fsm.context import FSMContext

FSM_UI_MESSAGE_ID = "_ui_message_id"


async def save_fsm_ui_message(state: FSMContext, message_id: int):
    await state.update_data(**{FSM_UI_MESSAGE_ID: message_id})


async def clear_fsm_ui(state: FSMContext, bot, chat_id: int):
    data = await state.get_data()
    msg_id = data.get(FSM_UI_MESSAGE_ID)

    if msg_id:
        try:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=msg_id,
                reply_markup=None
            )
        except Exception:
            pass
