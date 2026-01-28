from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import logging
from core.shutdown import shutdown_event

from database import get_pool

from services.user_service import recalculate_total_confirmed_days
from services.user_service import update_user_streak
from services.xp_service import add_xp_for_confirmation

from services.habit_view_service import send_habit_card, build_active_list

from repositories.affiliate_repository import (
    get_affiliate_for_user,
    mark_referral_active,
    add_payment_to_affiliate
)

from services.confirm_habit_service import habit_service
from services.message_queue import QUEUE_CONFIRM


router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class ConfirmHabitFSM(StatesGroup):
    waiting_for_media = State()


def cancel_kb(habit_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_media_{habit_id}")]
        ]
    )


# ================================
# 🔹 Старт подтверждения
# ================================
@router.callback_query(
    F.data.startswith("confirm_") & ~F.data.startswith("confirm_no_media_")
)
async def confirm_habit_start(callback: types.CallbackQuery, state: FSMContext):

    habit_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    logging.info(f"[CONFIRM] Пользователь {user_id} начал подтверждение привычки {habit_id}")

    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await habit_service.start_confirmation(conn, user_id, habit_id)

        if result.get("error") == "HABIT_NOT_FOUND":
            logging.warning(f"[CONFIRM] Привычка {habit_id} не найдена у пользователя {user_id}")
            await callback.answer("❌ Привычка не найдена.", show_alert=True)
            return

        reverify = result["reverify"]
        logging.info(f"[CONFIRM] reverify = {reverify} для пользователя {user_id}")

        await state.update_data(habit_id=habit_id, reverify=reverify)
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

        await state.update_data(confirm_message_id=sent.message_id)



# ================================
# 🔹 Отмена подтверждения
# ================================
@router.callback_query(F.data.startswith("cancel_media_"))
async def cancel_media(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logging.info(f"[CONFIRM] Пользователь {user_id} отменил подтверждение привычки")

    await state.clear()
    await callback.message.edit_text("❎ Подтверждение отменено.")
    await callback.answer()


# ================================
# 🔹 Получаем медиафайл
# ================================
@router.message(ConfirmHabitFSM.waiting_for_media)
async def receive_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    habit_id = data["habit_id"]
    reverify = data["reverify"]
    user_id = message.from_user.id

    logging.info(f"[MEDIA] Пользователь {user_id} отправил медиа для привычки {habit_id}")

    # PHOTO
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
        logging.info(f"[MEDIA] Фото получено. file_id={file_id}")

    # VIDEO + SIZE CHECK
    elif message.video:
        max_video_size = 25 * 1024 * 1024  # 25 MB
        video_size = message.video.file_size or 0

        logging.info(f"[MEDIA] Видео получено. file_id={message.video.file_id}, size={video_size} bytes")

        if video_size > max_video_size:
            logging.warning(f"[MEDIA] Видео отклонено! Размер {video_size} > {max_video_size}")
            await message.answer("⚠️ Видео слишком большое. Максимум — 25 МБ.")
            return

        file_id = message.video.file_id
        file_type = "video"

    # CIRCLE VIDEO
    elif message.video_note:
        file_id = message.video_note.file_id
        file_type = "circle"
        logging.info(f"[MEDIA] Кружочек получен. file_id={file_id}")

    else:
        logging.warning(f"[MEDIA] Пользователь {user_id} прислал неподдерживаемый тип")
        await message.answer("⚠️ Нужно фото, видео или кружочек 🎥")
        return


    # Добавляем задачу в очередь
    logging.info(f"[QUEUE] Добавляем задачу в очередь: user={user_id}, habit={habit_id}, type={file_type}")

    # 🔥 УБИРАЕМ КНОПКИ
    await clear_confirm_buttons(
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

@router.callback_query(F.data.startswith("confirm_no_media_"))
async def confirm_no_media(callback: types.CallbackQuery, state: FSMContext):
    habit_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id

    # 🔥 УБИРАЕМ КНОПКИ
    await clear_confirm_buttons(
        state=state,
        bot=callback.bot,
        chat_id=callback.message.chat.id
    )

    logging.info(f"[CONFIRM_NO_MEDIA] user={user_id}, habit={habit_id}")

    # FSM больше не нужен
    await state.clear()

    pool = await get_pool()
    async with pool.acquire() as conn:

        # 🔥 1. Проверка и reverify
        start = await habit_service.start_confirmation(conn, user_id, habit_id)

        if start.get("error") == "HABIT_NOT_FOUND":
            await callback.answer("❌ Привычка не найдена.", show_alert=True)
            return

        reverify = start["reverify"]

    # 🔥 2. КЛАДЁМ В ОЧЕРЕДЬ (КАК БУДТО ЭТО МЕДИА)
    await QUEUE_CONFIRM.put({
        "user_id": user_id,
        "habit_id": habit_id,
        "reverify": reverify,
        "file_id": None,
        "file_type": None,
        "chat_id": callback.message.chat.id,
        "reply_to": callback.message.message_id
    })
    await callback.answer("⏳ Подтверждение принято")


# ================================
# 🔥 Обработчик очереди (SAFE VERSION)
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

        FREE_MAIN_CHAT = -1002375148535

        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await habit_service.process_confirmation_media(
                conn=conn,
                user_id=user_id,
                habit_id=habit_id,
                file_id=file_id,
                file_type=file_type,
                reverify=reverify,
            )

        # ❌ привычка не найдена / уже завершена
        if result.get("error"):
            await bot.send_message(
                chat_id=chat_id,
                text="⚠️ Эта привычка уже завершена.",
                reply_to_message_id=reply_to
            )
            return

        # 👤 сообщение пользователю
        if result.get("self_message"):
            await bot.send_message(
                chat_id=chat_id,
                text=result["self_message"],
                parse_mode="Markdown",
                reply_to_message_id=reply_to
            )

        caption_text = result["caption_text"]
        share_allowed = result["share_allowed"]

        # 🔥 подтверждение без фото
        if file_type is None:
            await bot.send_message(
                FREE_MAIN_CHAT,
                caption_text,
                parse_mode="Markdown"
            )
            return

        # 🚫 медиа запрещено
        if not share_allowed:
            await bot.send_message(
                FREE_MAIN_CHAT,
                caption_text,
                parse_mode="Markdown"
            )
            return

        # 📸 фото
        if file_type == "photo":
            await bot.send_photo(
                FREE_MAIN_CHAT,
                file_id,
                caption=caption_text,
                parse_mode="Markdown"
            )

        # 🎥 видео
        elif file_type == "video":
            await bot.send_video(
                FREE_MAIN_CHAT,
                file_id,
                caption=caption_text,
                parse_mode="Markdown"
            )

        # ⭕ кружок
        elif file_type == "circle":
            await bot.send_video_note(FREE_MAIN_CHAT, file_id)
            await bot.send_message(
                FREE_MAIN_CHAT,
                caption_text,
                parse_mode="Markdown"
            )

        logging.info(f"[SEND] Медиа отправлено в чат {FREE_MAIN_CHAT}")

        # 🎯 сообщение о завершении челленджа
        if result.get("challenge_message"):
            await bot.send_message(
                chat_id=chat_id,
                text=result["challenge_message"],
                parse_mode="Markdown",
                reply_to_message_id=reply_to
            )

    except Exception as e:
        logging.error(f"[QUEUE PROCESSING ERROR] {e}", exc_info=True)
        try:
            await bot.send_message(
                chat_id=task["chat_id"],
                text="⚠️ Ошибка обработки подтверждения. Мы уже исправляем это."
            )
        except Exception:
            pass


# 🔥 ОЧИЩЕНИЕ КЛАВИАТУРЫ ПОСЛЕ ВЫПОЛНЕНИЯ ДЕЙСТВИЯ
async def clear_confirm_buttons(state: FSMContext, bot, chat_id: int):
    data = await state.get_data()
    msg_id = data.get("confirm_message_id")

    if msg_id:
        try:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=msg_id,
                reply_markup=None
            )
        except Exception:
            pass
