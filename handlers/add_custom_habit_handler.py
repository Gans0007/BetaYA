from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from database import get_pool

router = Router()

# -------------------------------
# 🔹 Состояния FSM
# -------------------------------
class AddHabit(StatesGroup):
    name = State()
    description = State()
    days = State()
    difficulty = State()  # 🔥 новая стадия выбора сложности
    confirm = State()


# -------------------------------
# 🔹 Клавиатура отмены
# -------------------------------
def cancel_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")]]
    )


# -------------------------------
# 🔹 Обработка нажатия “Отмена”
# -------------------------------
@router.callback_query(F.data == "cancel_fsm")
async def cancel_fsm(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❎ Создание привычки отменено.")
    await callback.answer()


# -------------------------------
# 🔹 Запуск процесса добавления
# -------------------------------
@router.callback_query(F.data == "add_custom_habit")
async def start_add_habit(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AddHabit.name)
    await callback.message.edit_text("✏️ Введи название своей привычки:", reply_markup=cancel_kb())
    await callback.answer()


# -------------------------------
# 🔹 Шаг 1 — Название
# -------------------------------
@router.message(AddHabit.name)
async def set_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddHabit.description)
    await message.answer("💬 Опиши коротко свою привычку:", reply_markup=cancel_kb())


# -------------------------------
# 🔹 Шаг 2 — Описание
# -------------------------------
@router.message(AddHabit.description)
async def set_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddHabit.days)
    await message.answer("📅 На сколько дней хочешь взять эту привычку? (минимум 7)", reply_markup=cancel_kb())


# -------------------------------
# 🔹 Шаг 3 — Длительность
# -------------------------------
@router.message(AddHabit.days)
async def set_days(message: types.Message, state: FSMContext):
    try:
        days = int(message.text)
        if days < 7 or days > 365:
            raise ValueError
    except ValueError:
        await message.answer("⚠️ Введи число от 7 до 365. Минимум — неделя 💪", reply_markup=cancel_kb())
        return

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

    await message.answer(
        "🎯 Выбери уровень сложности привычки:\n\n"
        "⭐ — можно пропускать, без аннулирования\n"
        "⭐⭐ — сброс, если пропущено 2 дня подряд\n"
        "⭐⭐⭐ — сброс, если пропущен хоть 1 день\n",
        reply_markup=keyboard
    )


# -------------------------------
# 🔹 Шаг 4 — Выбор сложности
# -------------------------------
@router.callback_query(F.data.startswith("diff_"))
async def set_difficulty(callback: types.CallbackQuery, state: FSMContext):
    diff = int(callback.data.split("_")[1])
    await state.update_data(difficulty=diff)

    data = await state.get_data()
    name = data["name"]
    desc = data["description"]
    days = data["days"]

    diff_text = {1: "⭐ Легко", 2: "⭐⭐ Средне", 3: "⭐⭐⭐ Сложно"}[diff]

    text = (
        f"📝 *Проверь данные привычки:*\n\n"
        f"🏁 *Название:* {name}\n"
        f"📖 *Описание:* {desc}\n"
        f"📅 *Длительность:* {days} дней\n"
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

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await state.set_state(AddHabit.confirm)
    await callback.answer()


# -------------------------------
# 🔹 Сохранение привычки
# -------------------------------
@router.callback_query(F.data == "save_habit")
async def save_habit(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    desc = data["description"]
    days = data["days"]
    diff = data["difficulty"]

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO habits (user_id, name, description, days, confirm_type, is_challenge, difficulty)
            VALUES ($1, $2, $3, $4, 'media', FALSE, $5)
        """, callback.from_user.id, name, desc, days, diff)

    await callback.message.edit_text(
        f"✅ Привычка *{name}* успешно сохранена!\n"
        f"Теперь она появится в твоих 📋 *Активных заданиях*.",
        parse_mode="Markdown"
    )
    await state.clear()
    await callback.answer()
