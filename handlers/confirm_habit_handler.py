from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging

from services.confirm_habit_service import habit_service
from services.message_queue import QUEUE_CONFIRM
from services.fsm_ui import save_fsm_ui_message, clear_fsm_ui
from config import PUBLIC_CHAT_ID

from core.database import get_pool
from services.achievements.achievements_service import process_achievements_and_notify


router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ================================
# 🔹 FSM
# ================================
class ConfirmHabitFSM(StatesGroup):
    waiting_for_media = State()


# ================================
# 🔹 Старт подтверждения
# ================================
@router.callback_query(
    F.data.startswith("confirm_") & ~F.data.startswith("confirm_no_media_")
)
async def confirm_habit_start(callback: types.CallbackQuery, state: FSMContext):
    habit_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    logging.info(f"[CONFIRM] user={user_id} habit={habit_id}")

    result = await habit_service.start_confirmation(user_id, habit_id)

    if result.get("error") == "HABIT_NOT_FOUND":
        await callback.answer("❌ Привычка не найдена.", show_alert=True)
        return

    await state.update_data(
        habit_id=habit_id,
        reverify=result["reverify"]
    )
    await state.set_state(ConfirmHabitFSM.waiting_for_media)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить без фото",
                    callback_data=f"confirm_no_media_{habit_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data=f"cancel_media_{habit_id}"
                )
            ]
        ]
    )

    sent = await callback.message.answer(
        result["text"],
        parse_mode=result.get("parse_mode"),
        reply_markup=keyboard
    )

    await save_fsm_ui_message(state, sent.message_id)
    await callback.answer()


# ================================
# 🔹 Отмена подтверждения
# ================================
@router.callback_query(F.data.startswith("cancel_media_"))
async def cancel_media(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"[CONFIRM CANCEL] user={callback.from_user.id}")

    await clear_fsm_ui(
        state=state,
        bot=callback.bot,
        chat_id=callback.message.chat.id
    )

    await state.clear()
    await callback.answer()
    await callback.message.answer("❎ Подтверждение отменено.")


# ================================
# 🔹 Получаем медиа
# ================================
@router.message(ConfirmHabitFSM.waiting_for_media)
async def receive_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    habit_id = data["habit_id"]
    reverify = data["reverify"]
    user_id = message.from_user.id

    # ---- тип медиа ----
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"

    elif message.video:
        if (message.video.file_size or 0) > 25 * 1024 * 1024:
            await message.answer("⚠️ Видео слишком большое (макс 25 МБ)")
            return
        file_id = message.video.file_id
        file_type = "video"

    elif message.video_note:
        file_id = message.video_note.file_id
        file_type = "circle"

    else:
        await message.answer("⚠️ Нужно фото, видео или кружочек")
        return

    # 🔥 закрываем FSM UI
    await clear_fsm_ui(
        state=state,
        bot=message.bot,
        chat_id=message.chat.id
    )

    await QUEUE_CONFIRM.put({
        "user_id": user_id,
        "habit_id": habit_id,
        "reverify": reverify,
        "file_id": file_id,
        "file_type": file_type,
        "chat_id": message.chat.id,
        "reply_to": message.message_id
    })

    await message.answer("⏳ Подтверждение принято в обработку...")
    await state.clear()


# ================================
# 🔹 Подтверждение без фото
# ================================
@router.callback_query(F.data.startswith("confirm_no_media_"))
async def confirm_no_media(callback: types.CallbackQuery, state: FSMContext):
    habit_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id

    await clear_fsm_ui(
        state=state,
        bot=callback.bot,
        chat_id=callback.message.chat.id
    )
    await state.clear()

    start = await habit_service.start_confirmation(user_id, habit_id)

    if start.get("error") == "HABIT_NOT_FOUND":
        await callback.answer("❌ Привычка не найдена.", show_alert=True)
        return

    await QUEUE_CONFIRM.put({
        "user_id": user_id,
        "habit_id": habit_id,
        "reverify": start["reverify"],
        "file_id": None,
        "file_type": None,
        "chat_id": callback.message.chat.id,
        "reply_to": callback.message.message_id
    })

    await callback.answer("⏳ Подтверждение принято")


# ================================
# 🔥 Обработчик очереди
# ================================
async def process_task_from_queue(task, bot):
    try:
        user_id = task["user_id"]
        habit_id = task["habit_id"]
        reverify = task["reverify"]
        file_id = task["file_id"]
        file_type = task["file_type"]
        chat_id = task["chat_id"]
        reply_to = task["reply_to"]

        PUBLIC_CHAT_ID

        result = await habit_service.process_confirmation_media(
            user_id=user_id,
            habit_id=habit_id,
            file_id=file_id,
            file_type=file_type,
            reverify=reverify,
        )

        if result.get("error"):
            await bot.send_message(
                chat_id=chat_id,
                text="⚠️ Эта привычка уже завершена.",
                reply_to_message_id=reply_to
            )
            return

#--------

        if result.get("self_message"):
            await bot.send_message(
                chat_id=chat_id,
                text=result["self_message"],
                parse_mode="Markdown",
                reply_to_message_id=reply_to
            )

        caption_text = result["caption_text"]
        share_allowed = result["share_allowed"]

        if file_type is None or not share_allowed:
            await bot.send_message(
                PUBLIC_CHAT_ID,
                caption_text,
                parse_mode="Markdown"
            )
        else:
            if file_type == "photo":
                await bot.send_photo(
                    PUBLIC_CHAT_ID,
                    file_id,
                    caption=caption_text,
                    parse_mode="Markdown"
                )

            elif file_type == "video":
                await bot.send_video(
                    PUBLIC_CHAT_ID,
                    file_id,
                    caption=caption_text,
                    parse_mode="Markdown"
                )

            elif file_type == "circle":
                await bot.send_video_note(PUBLIC_CHAT_ID, file_id)
                await bot.send_message(
                    PUBLIC_CHAT_ID,
                    caption_text,
                    parse_mode="Markdown"
                )

        if result.get("challenge_message"):
            await bot.send_message(
                chat_id=chat_id,
                text=result["challenge_message"],
                parse_mode="Markdown",
                reply_to_message_id=reply_to
            )

        # ================================
        # 🏆 Централизованная проверка достижений
        # ================================
        pool = await get_pool()
        async with pool.acquire() as conn:
            await process_achievements_and_notify(
                bot,
                conn,
                user_id,
                trigger_types=["streak", "total_confirms", "challenge_complete"]
            )

    except Exception as e:
        logging.error(f"[QUEUE PROCESS ERROR] {e}", exc_info=True)
        try:
            await bot.send_message(
                chat_id=task["chat_id"],
                text="⚠️ Ошибка обработки подтверждения."
            )
        except Exception:
            pass
