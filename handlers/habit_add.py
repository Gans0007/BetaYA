import os
import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from states.habit_states import HabitForm
from services.habits.habit_service import save_habit

logger = logging.getLogger(__name__)
router = Router()

cancel_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm_habit")]]
)

# ✅ Обработка кнопки "➕ Добавить привычку"
@router.callback_query(lambda c: c.data == "add_habit_custom")
async def callback_start_habit(callback: CallbackQuery, state: FSMContext):
    logger.info(f"[{callback.from_user.id}] Нажал на ➕ Добавить привычку")
    await callback.message.answer("✍️ Введи название привычки (например: Бег):", reply_markup=cancel_keyboard)
    await state.set_state(HabitForm.name)
    await callback.answer()

# 1. Название привычки
@router.message(HabitForm.name)
async def process_name(message: Message, state: FSMContext):
    logger.info(f"[{message.from_user.id}] Ввел название привычки: {message.text}")
    await state.update_data(name=message.text)
    await message.answer("📅 Сколько дней ты хочешь придерживаться этой привычки? (например: 20):", reply_markup=cancel_keyboard)
    await state.set_state(HabitForm.days)

# 2. Длительность (с проверкой на цифры)
@router.message(HabitForm.days)
async def process_days(message: Message, state: FSMContext):
    if not message.text.isdigit():
        logger.warning(f"[{message.from_user.id}] Ввел нецифровое значение дней: {message.text}")
        await message.answer("❌ Пожалуйста, введи количество дней только цифрами (например: 20).", reply_markup=cancel_keyboard)
        return

    logger.info(f"[{message.from_user.id}] Ввел длительность привычки: {message.text} дней")
    await state.update_data(days=int(message.text))
    await message.answer("📝 Введи короткое описание привычки (например: Бегать каждый день не меньше километра):", reply_markup=cancel_keyboard)
    await state.set_state(HabitForm.description)

# 3. Описание
@router.message(HabitForm.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    logger.info(f"[{message.from_user.id}] Ввел описание привычки")

    summary = (
        f"✅ <b>Готово!</b> Вот что ты указал:\n\n"
        f"<b>Название:</b> {data['name']}\n"
        f"<b>Длительность:</b> {data['days']} дней\n"
        f"<b>Описание:</b> {data['description']}\n\n"
        f"🧠 Я буду ежедневно напоминать тебе об этой привычке, чтобы ты не сбивался с пути.\n\n"
        f"👇 <b>Сохранить привычку или удалить?</b>"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Сохранить", callback_data="save_habit")],
        [InlineKeyboardButton(text="❌ Удалить", callback_data="cancel_habit")]
    ])

    logger.info(f"[{message.from_user.id}] Подтвердительная карточка сформирована: {data}")
    await message.answer(summary, reply_markup=keyboard, parse_mode="HTML")

# ✅ Сохранение привычки в БД
@router.callback_query(lambda c: c.data == "save_habit")
async def confirm_habit(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    logger.info(f"[{user_id}] Подтверждает сохранение привычки: {data}")

    try:
        await save_habit(
            user_id=user_id,
            name=data['name'],
            days=int(data['days']),
            description=data['description']
        )
        await callback.message.edit_text("🔥 Привычка сохранена и добавлена в активные задания!")
        logger.info(f"[{user_id}] Привычка сохранена успешно в БД")

    except Exception as e:
        logger.exception(f"[{user_id}] Ошибка при сохранении привычки: {e}")
        await callback.message.edit_text(f"❌ Ошибка при сохранении привычки: {e}")

    finally:
        await state.clear()
        await callback.answer()

# ❌ Отмена создания привычки (в конце)
@router.callback_query(lambda c: c.data == "cancel_habit")
async def cancel_habit(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info(f"[{user_id}] Отменил создание привычки (финальный этап)")
    await state.clear()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить привычку", callback_data="add_habit_custom")],
        [InlineKeyboardButton(text="🔥 Взять Challenge", callback_data="take_challenge")]
    ])

    await callback.message.edit_text(
        "🚫 Привычка удалена.\n\n"
        "Выбери, что хочешь сделать дальше:",
        reply_markup=keyboard
    )
    await callback.answer()

# ❌ Отмена FSM на любом этапе
@router.callback_query(lambda c: c.data == "cancel_fsm_habit")
async def cancel_fsm_creation(callback: CallbackQuery, state: FSMContext):
    logger.info(f"[{callback.from_user.id}] Отменил FSM-добавление привычки")
    await state.clear()
    await callback.message.edit_text("🚫 Добавление привычки отменено.")
    await callback.answer()
