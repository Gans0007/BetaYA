from aiogram import Router, F, types
import random  
from datetime import datetime, timezone
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from data.challenges_data import FINAL_MESSAGES  
import pytz
import logging

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
@router.callback_query(F.data.startswith("confirm_"))
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

        await callback.message.answer(
            result["text"],
            parse_mode=result.get("parse_mode"),
            reply_markup=cancel_kb(habit_id)
        )

    await callback.answer()


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

    await QUEUE_CONFIRM.put({
        "user_id": user_id,
        "habit_id": habit_id,
        "reverify": reverify,
        "file_id": file_id,
        "file_type": file_type,
        "message": message
    })

    await message.answer("⏳ Подтверждение принято в обработку...")
    await state.clear()


# ================================
# 🔥 Обработчик очереди (НОВАЯ ЛОГИКА)
# ================================
async def process_task_from_queue(task):
    message = task["message"]
    user_id = task["user_id"]
    habit_id = task["habit_id"]
    reverify = task["reverify"]
    file_id = task["file_id"]
    file_type = task["file_type"]

    FREE_MAIN_CHAT = -1002375148535
    # FREE_EXTRA_CHAT = -1002435430482 

    logging.info(f"[QUEUE] Начата обработка задачи: user={user_id}, habit={habit_id}, type={file_type}")

    pool = await get_pool()
    async with pool.acquire() as conn:
        try:
            result = await habit_service.process_confirmation_media(
                conn=conn,
                user_id=user_id,
                habit_id=habit_id,
                file_id=file_id,
                file_type=file_type,
                reverify=reverify,
            )

            if result.get("error"):
                logging.warning(f"[QUEUE] Ошибка: привычка {habit_id} не найдена")
                await message.answer("⚠️ Эта привычка уже завершена.")
                return

            logging.info(f"[QUEUE] Сообщение пользователю отправлено.")

            caption_text = result["caption_text"]
            share_allowed = result["share_allowed"]

            async def send_to_chat(chat_id):
                logging.info(f"[SEND] Отправка в чат {chat_id} (type={file_type})")

                if not share_allowed:
                    await message.bot.send_message(chat_id, caption_text, parse_mode="Markdown")
                    logging.info(f"[SEND] Текст отправлен в чат {chat_id}")
                    return

                if file_type == "photo":
                    await message.bot.send_photo(chat_id, file_id, caption=caption_text, parse_mode="Markdown")
                elif file_type == "video":
                    await message.bot.send_video(chat_id, file_id, caption=caption_text, parse_mode="Markdown")
                elif file_type == "circle":
                    await message.bot.send_video_note(chat_id, file_id)
                    await message.bot.send_message(chat_id, caption_text, parse_mode="Markdown")

                logging.info(f"[SEND] Медиа отправлено в чат {chat_id}")

            await send_to_chat(FREE_MAIN_CHAT)

            # 🔥 И автоматически дублируем в дополнительный чат
            #logging.info(f"[SEND] Дублирование медиа в дополнительный чат {FREE_EXTRA_CHAT}")
            #await send_to_chat(FREE_EXTRA_CHAT)

            if result.get("challenge_message"):
                logging.info(f"[CHALLENGE] Челлендж завершен, отправляем уведомление.")
                await message.answer(result["challenge_message"], parse_mode="Markdown")

        except Exception as e:
            logging.error(f"[QUEUE PROCESSING ERROR] {e}", exc_info=True)
            await message.answer("⚠️ Ошибка обработки подтверждения. Мы исправим это.")
