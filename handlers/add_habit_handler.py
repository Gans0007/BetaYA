from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


@router.message(lambda message: message.text == "➕ Добавить привычку / челлендж")
async def add_habit_menu(message: types.Message):
    user_id = message.from_user.id
    logging.info(f"[ADD] Пользователь {user_id} открыл меню добавления")

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
