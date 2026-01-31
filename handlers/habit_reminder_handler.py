from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import time, datetime

from services.fsm_ui import save_fsm_ui_message, clear_fsm_ui

import pytz
import re
import logging

from database import get_pool

router = Router()
logger = logging.getLogger(__name__)

TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


class HabitReminderFSM(StatesGroup):
    waiting_for_time = State()


# ================================
# 🔔 Нажатие на кнопку "Напоминание"
# ================================
@router.callback_query(F.data.startswith("set_reminder_"))
async def set_reminder_start(callback: types.CallbackQuery, state: FSMContext):
    habit_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id

    await state.update_data(habit_id=habit_id)

    # 🔹 Получаем таймзону пользователя
    pool = await get_pool()
    async with pool.acquire() as conn:
        habit_row = await conn.fetchrow("""
            SELECT h.reminder_time, u.timezone
            FROM habits h
            JOIN users u ON u.user_id = h.user_id
            WHERE h.id = $1
        """, habit_id)

    tz_name = habit_row["timezone"] if habit_row and habit_row["timezone"] else "Europe/Kyiv"
    reminder_time_exists = habit_row and habit_row["reminder_time"] is not None

    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = pytz.timezone("Europe/Kyiv")

    now_local = datetime.now(tz).strftime("%H:%M")

    # 🔴 КНОПКИ: Отмена + Удалить напоминание
    buttons = [
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="cancel_reminder_setup"
        )
    ]

    # 🧠 Кнопка "Удалить" — только если напоминание есть
    if reminder_time_exists:
        buttons.append(
            InlineKeyboardButton(
                text="🗑 Удалить напоминание",
                callback_data="reminder_delete"
            )
        )

    action_kb = InlineKeyboardMarkup(
        inline_keyboard=[buttons]
    )

    sent = await callback.message.answer(
        "⏰ Введите время напоминания в формате HH:MM\n"
        "Пример: 07:30 или 21:45\n\n"
        f"🕒 Текущее время: *{now_local}* ({tz.zone})",
        parse_mode="Markdown",
        reply_markup=action_kb
    )

    # 🧠 сохраняем UI-сообщение в FSM
    await save_fsm_ui_message(state, sent.message_id)


    await state.set_state(HabitReminderFSM.waiting_for_time)
    await callback.answer()


# ================================
# ⌨️ Ввод времени
# ================================
@router.message(HabitReminderFSM.waiting_for_time)
async def set_reminder_time(message: types.Message, state: FSMContext):
    text = message.text.strip()

    if not TIME_PATTERN.match(text):
        await message.answer("❌ Неверный формат. Используйте HH:MM (например, 08:30)")
        return

    hour, minute = map(int, text.split(":"))
    reminder_time = time(hour=hour, minute=minute)

    data = await state.get_data()
    habit_id = data["habit_id"]
    user_id = message.from_user.id

    pool = await get_pool()
    async with pool.acquire() as conn:
        # 🔹 Получаем название привычки и таймзону
        habit_row = await conn.fetchrow("""
            SELECT h.name, u.timezone
            FROM habits h
            JOIN users u ON u.user_id = h.user_id
            WHERE h.id = $1
        """, habit_id)

        await conn.execute(
            """
            UPDATE habits
            SET reminder_time = $1
            WHERE id = $2
            """,
            reminder_time,
            habit_id
        )

    habit_name = habit_row["name"]
    tz_name = habit_row["timezone"] or "Europe/Kyiv"

    # 🔔 ЛОГ УСТАНОВКИ НАПОМИНАНИЯ
    logger.info(
        f"[REMINDER SET] Напоминание пользователю {user_id} "
        f'на привычку "{habit_name}" '
        f"установлено на {text} ({tz_name})"
    )

    # 🧹 убираем кнопки FSM
    await clear_fsm_ui(
        state=state,
        bot=message.bot,
        chat_id=message.chat.id
    )

    await message.answer(
        f"🔔 Напоминание установлено ежедневно в {text}"
    )

    await state.clear()


# ================================
# ❌ Отмена установки напоминания
# ================================
@router.callback_query(F.data == "cancel_reminder_setup")
async def cancel_reminder_setup(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text(
        "⛔️ Установка напоминания отменена"
    )

    await callback.answer()

# ================================
# 🗑 Удалить напоминание
# ================================
@router.callback_query(F.data == "reminder_delete")
async def delete_habit_reminder(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    habit_id = data.get("habit_id")
    user_id = callback.from_user.id

    if not habit_id:
        await callback.answer("Не удалось определить привычку", show_alert=True)
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        habit_row = await conn.fetchrow("""
            SELECT h.name, u.timezone
            FROM habits h
            JOIN users u ON u.user_id = h.user_id
            WHERE h.id = $1
        """, habit_id)

        if not habit_row:

            await clear_fsm_ui(
                state=state,
                bot=callback.bot,
                chat_id=callback.message.chat.id
            )

            await state.clear()
            await callback.message.edit_text("⚠️ Привычка не найдена")
            await callback.answer()
            return

        await conn.execute("""
            UPDATE habits
            SET reminder_time = NULL
            WHERE id = $1
        """, habit_id)

    habit_name = habit_row["name"]
    tz_name = habit_row["timezone"] or "Europe/Kyiv"

    # 🪵 ЛОГ УДАЛЕНИЯ
    logger.info(
        f"[REMINDER DELETED] Напоминание пользователю {user_id} "
        f'на привычку "{habit_name}" удалено ({tz_name})'
    )

    await state.clear()

    await callback.message.edit_text(
        "🗑 Напоминание удалено"
    )

    await callback.answer()


