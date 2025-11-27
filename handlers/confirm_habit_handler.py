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


# ================================
# 🔥 1) Запрос подтверждения удаления привычки
#     Срабатывает по кнопке ask_delete_<id>
# ================================
@router.callback_query(F.data.startswith("ask_delete_"))
async def ask_delete(callback: types.CallbackQuery):
    # Получаем id привычки
    habit_id = int(callback.data.split("_")[2])

    # Клавиатура: Да / Отмена
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Да, удалить", callback_data=f"delete_habit_{habit_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="dismiss_delete")]
        ]
    )

    # Показываем вопрос
    await callback.message.edit_text(
        "❗ Ты точно хочешь удалить эту привычку?",
        reply_markup=kb
    )

    await callback.answer()


# ================================
# 🔥 2) Удаление привычки
#     Срабатывает по кнопке delete_habit_<id>
# ================================
@router.callback_query(F.data.startswith("delete_habit_"))
async def delete_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    pool = await get_pool()

    async with pool.acquire() as conn:

        # 🟦 1. Считаем количество привычек ДО удаления
        before_rows = await conn.fetch("""
            SELECT id FROM habits
            WHERE user_id=$1 AND is_active=TRUE
        """, user_id)
        before_count = len(before_rows)

        # ---------------------------------------------------
        # 🟦 2. Удаляем привычку + её подтверждения
        # ---------------------------------------------------
        await conn.execute("DELETE FROM confirmations WHERE habit_id=$1", habit_id)
        await conn.execute("DELETE FROM habits WHERE id=$1 AND user_id=$2", habit_id, user_id)

        # ---------------------------------------------------
        # 🟦 3. Грузим привычки ПОСЛЕ удаления
        # ---------------------------------------------------
        habits = await conn.fetch("""
            SELECT h.id, h.name, h.description, h.days, h.done_days,
                   h.is_challenge, h.difficulty,
                   (SELECT datetime FROM confirmations
                        WHERE habit_id=h.id
                        ORDER BY datetime DESC LIMIT 1) AS last_date,
                   u.timezone
            FROM habits h
            JOIN users u ON u.user_id=h.user_id
            WHERE h.user_id=$1 AND h.is_active=TRUE
            ORDER BY h.is_challenge DESC, h.created_at DESC
        """, user_id)

    # ---------------------------------------------------
    # 🟥 0 привычек осталось
    # ---------------------------------------------------
    if before_count == 1:
        await callback.message.edit_text(
            "🗑 Привычка удалена.\n\n😴 Больше нет активных привычек."
        )
        await callback.answer()
        return

    # ---------------------------------------------------
    # 🟧 Было 2 → стало 1 → показываем карточка удалена
    # ---------------------------------------------------
    if before_count == 2:
        await callback.message.edit_text(
            "🗑 Привычка удалена."
        )
        await callback.answer()
        return

    # ---------------------------------------------------
    # 🟨 Было 3 → стало 2 → показываем 2 карточки
    # ---------------------------------------------------
    if before_count == 3:
        await callback.message.delete()
        for h in habits:
            await send_habit_card(callback.message.chat, h, user_id)
        await callback.answer()
        return

    # ---------------------------------------------------
    # 🟩 Было 4+ → показываем список
    # ---------------------------------------------------
    if before_count >= 4:
        try:
            await callback.message.delete()
        except:
            pass

        text, kb, _ = await build_active_list(user_id)
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=kb)
        await callback.answer()
        return


# ================================
# 🔥 3) Отмена удаления привычки
# ================================
@router.callback_query(F.data == "dismiss_delete")
async def dismiss_delete(callback: types.CallbackQuery):
    # Возвращаем обычное сообщение
    await callback.message.edit_text("Отменено ❎")
    await callback.answer()
