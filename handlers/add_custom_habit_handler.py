from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

from services.habit_create_service import create_custom_habit

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


# -------------------------------
# 🔹 FSM States
# -------------------------------
class AddHabit(StatesGroup):
    name = State()
    description = State()
    days = State()
    difficulty = State()
    confirm = State()


def cancel_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")]]
    )


async def clear_previous_prompt(state: FSMContext, bot, chat_id: int):
    data = await state.get_data()
    last_msg_id = data.get("last_prompt_message_id")

    if last_msg_id:
        try:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=last_msg_id,
                reply_markup=None
            )
        except Exception:
            pass


# -------------------------------
# ❌ Отмена
# -------------------------------
@router.callback_query(F.data == "cancel_fsm")
async def cancel_fsm(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"[ADD HABIT] Пользователь {callback.from_user.id} отменил создание привычки")

    await clear_previous_prompt(state, callback.bot, callback.message.chat.id)
    await state.clear()
    await callback.answer()

    await callback.message.answer("❎ Создание привычки отменено.")


# -------------------------------
# ▶️ Старт
# -------------------------------
@router.callback_query(F.data == "add_custom_habit")
async def start_add_habit(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"[ADD HABIT] Пользователь {callback.from_user.id} начал создание привычки")

    await callback.answer()
    await state.set_state(AddHabit.name)

    sent = await callback.message.answer(
        "✏️ Введи название своей привычки:",
        reply_markup=cancel_kb()
    )

    await state.update_data(last_prompt_message_id=sent.message_id)


# -------------------------------
# ✍️ Имя
# -------------------------------
@router.message(AddHabit.name)
async def set_name(message: types.Message, state: FSMContext):
    await clear_previous_prompt(state, message.bot, message.chat.id)

    await state.update_data(name=message.text)
    await state.set_state(AddHabit.description)

    sent = await message.answer(
        "💬 Опиши коротко свою привычку:",
        reply_markup=cancel_kb()
    )

    await state.update_data(last_prompt_message_id=sent.message_id)


# -------------------------------
# 📝 Описание
# -------------------------------
@router.message(AddHabit.description)
async def set_description(message: types.Message, state: FSMContext):
    await clear_previous_prompt(state, message.bot, message.chat.id)

    await state.update_data(description=message.text)
    await state.set_state(AddHabit.days)

    sent = await message.answer(
        "📅 На сколько дней хочешь взять эту привычку? (минимум 7)",
        reply_markup=cancel_kb()
    )

    await state.update_data(last_prompt_message_id=sent.message_id)


# -------------------------------
# 📆 Дни
# -------------------------------
@router.message(AddHabit.days)
async def set_days(message: types.Message, state: FSMContext):
    try:
        days = int(message.text)
        if days < 7 or days > 365:
            raise ValueError
    except ValueError:
        sent = await message.answer(
            "⚠️ Введи число от 7 до 365. Минимум — неделя 💪",
            reply_markup=cancel_kb()
        )
        await state.update_data(last_prompt_message_id=sent.message_id)
        return

    await clear_previous_prompt(state, message.bot, message.chat.id)

    await state.update_data(days=days)
    await state.set_state(AddHabit.difficulty)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐ Легко", callback_data="diff_1"),
                InlineKeyboardButton(text="⭐⭐ Средне", callback_data="diff_2"),
                InlineKeyboardButton(text="⭐⭐⭐ Сложно", callback_data="diff_3"),
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")]
        ]
    )

    sent = await message.answer(
        "🎯 Выбери уровень сложности привычки:",
        reply_markup=keyboard
    )

    await state.update_data(last_prompt_message_id=sent.message_id)


# -------------------------------
# 🎯 Сложность
# -------------------------------
@router.callback_query(F.data.startswith("diff_"))
async def set_difficulty(callback: types.CallbackQuery, state: FSMContext):
    await clear_previous_prompt(state, callback.bot, callback.message.chat.id)

    diff = int(callback.data.split("_")[1])
    await state.update_data(difficulty=diff)

    data = await state.get_data()

    diff_text = {1: "⭐ Легко", 2: "⭐⭐ Средне", 3: "⭐⭐⭐ Сложно"}[diff]

    text = (
        f"📝 *Проверь данные привычки:*\n\n"
        f"🏁 *Название:* {data['name']}\n"
        f"📖 *Описание:* {data['description']}\n"
        f"📅 *Длительность:* {data['days']} дней\n"
        f"🎯 *Сложность:* {diff_text}\n\n"
        f"Сохранить эту привычку?"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Сохранить", callback_data="save_habit"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")
            ]
        ]
    )

    sent = await callback.message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    await state.set_state(AddHabit.confirm)
    await state.update_data(last_prompt_message_id=sent.message_id)
    await callback.answer()


# -------------------------------
# 💾 Сохранение
# -------------------------------
@router.callback_query(F.data == "save_habit")
async def save_habit(callback: types.CallbackQuery, state: FSMContext):
    await clear_previous_prompt(state, callback.bot, callback.message.chat.id)

    data = await state.get_data()
    name = data["name"]

    await create_custom_habit(
        user_id=callback.from_user.id,
        data=data
    )

    await callback.answer()
    await callback.message.answer(
        f"✅ Привычка *{name}* успешно сохранена!\n"
        f"Теперь она появится в твоих 📋 *Активных заданиях*.",
        parse_mode="Markdown"
    )

    await state.clear()
