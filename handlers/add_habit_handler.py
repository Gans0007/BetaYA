from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.message(lambda message: message.text == "➕ Добавить привычку / челлендж")
async def add_habit_menu(message: types.Message):
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
