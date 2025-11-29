from aiogram import Router, F, types
import random  # может больше не нужен, но оставлю как в оригинале
from datetime import datetime, timezone
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from data.challenges_data import FINAL_MESSAGES  # используется теперь в сервисе, но оставлю импорт

import pytz

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


router = Router()


# ================================
# 🔹 FSM состояния
# ================================
class ConfirmHabitFSM(StatesGroup):
    waiting_for_media = State()


# ================================
# 🔹 Кнопка отмены
# ================================
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

    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await habit_service.start_confirmation(conn, user_id, habit_id)

        if result.get("error") == "HABIT_NOT_FOUND":
            await callback.answer("❌ Привычка не найдена.", show_alert=True)
            return

        reverify = result["reverify"]

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

    # Определяем тип медиа
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.video_note:
        file_id = message.video_note.file_id
        file_type = "circle"
    else:
        await message.answer("⚠️ Нужно фото, видео или кружочек 🎥")
        return

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

            if result.get("error") == "HABIT_NOT_FOUND":
                await message.answer("⚠️ Эта привычка уже завершена.")
                return

            # Сообщение пользователю (XP / переподтверждение и т.п.)
            await message.answer(result["self_message"])

            # =============================
            # 🔥 ОТПРАВКА В ЧАТ
            # =============================
            caption_text = result["caption_text"]
            target_chat = result["target_chat"]
            share_allowed = result["share_allowed"]

            if not share_allowed:
                await message.bot.send_message(
                    target_chat,
                    caption_text,
                    parse_mode="Markdown"
                )
            else:
                if file_type == "photo":
                    await message.bot.send_photo(
                        target_chat, file_id,
                        caption=caption_text,
                        parse_mode="Markdown"
                    )

                elif file_type == "video":
                    await message.bot.send_video(
                        target_chat, file_id,
                        caption=caption_text,
                        parse_mode="Markdown"
                    )

                elif file_type == "circle":
                    await message.bot.send_video_note(target_chat, file_id)
                    await message.bot.send_message(
                        target_chat,
                        caption_text,
                        parse_mode="Markdown"
                    )

            # ===========================================================
            # 🔥 Автозавершение челленджа — текст пользователю
            # ===========================================================
            if result.get("challenge_message"):
                await message.answer(result["challenge_message"], parse_mode="Markdown")

        finally:
            # 🧹 ВСЕГДА сбрасываем FSM — и больше он не залипнет
            await state.clear()
