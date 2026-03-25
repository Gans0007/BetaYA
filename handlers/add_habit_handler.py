from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


# 🔥 ЕДИНАЯ ФУНКЦИЯ ОТПРАВКИ
async def send_add_habit_menu(message: types.Message):
    text = (
        "📍 В «Привычки» ты можешь добавить свою собственную.\n"
        "🔥 А в «Challenge» — выбрать одно из заданий от команды Your Ambitions."
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить привычку", callback_data="add_custom_habit")],
            [InlineKeyboardButton(text="🔥 Взять из списка", callback_data="choose_from_list")],
        ]
    )

    await message.answer(text, reply_markup=keyboard)


# 🔹 СТАРАЯ КНОПКА (меню)
@router.message(lambda message: message.text == "➕ Добавить привычку / челлендж")
async def add_habit_menu(message: types.Message):
    await send_add_habit_menu(message)


# 🔥 INLINE КНОПКА ИЗ START
@router.callback_query(F.data == "open_add_menu")
async def open_add_menu(callback: types.CallbackQuery):
    await callback.answer()
    await send_add_habit_menu(callback.message)


# 🔙 НАЗАД В МЕНЮ
@router.callback_query(F.data == "back_to_add_menu")
async def back_to_add_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logging.info(f"[ADD] Пользователь {user_id} вернулся в меню добавления")

    text = (
        "📍 В «Привычки» ты можешь добавить свою собственную.\n"
        "🔥 А в «Challenge» — выбрать одно из заданий от команды Your Ambitions."
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить привычку", callback_data="add_custom_habit")],
            [InlineKeyboardButton(text="🔥 Взять из списка", callback_data="choose_from_list")],
        ]
    )

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()