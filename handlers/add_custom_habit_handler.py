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
    confirm = State()  # финальное подтверждение


# -------------------------------
# 🔹 Универсальная клавиатура отмены
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
# 🔹 Шаг 1 — Название привычки
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
# 🔹 Шаг 3 — Длительность и подтверждение
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
    data = await state.get_data()

    name = data["name"]
    desc = data["description"]

    # Формируем текст подтверждения
    text = (
        f"📝 *Проверь данные привычки:*\n\n"
        f"🏁 *Название:* {name}\n"
        f"📖 *Описание:* {desc}\n"
        f"📅 *Длительность:* {days} дней\n\n"
        f"Сохранить эту привычку?"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Сохранить", callback_data="save_habit"),
                InlineKeyboardButton(text="❌ Удалить", callback_data="cancel_habit")
            ]
        ]
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
    await state.set_state(AddHabit.confirm)


# -------------------------------
# 🔹 Кнопка ✅ Сохранить
# -------------------------------
@router.callback_query(F.data == "save_habit")
async def save_habit(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    desc = data["description"]
    days = data["days"]

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO habits (user_id, name, description, days, confirm_type, is_challenge)
            VALUES ($1, $2, $3, $4, 'media', FALSE)
        """, callback.from_user.id, name, desc, days)

    await callback.message.edit_text(
        f"✅ Привычка *{name}* успешно сохранена!\n"
        f"Теперь она появится в твоих 📋 *Активных заданиях*.",
        parse_mode="Markdown"
    )
    await state.clear()
    await callback.answer()


# -------------------------------
# 🔹 Кнопка ❌ Удалить
# -------------------------------
@router.callback_query(F.data == "cancel_habit")
async def cancel_habit(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Привычка удалена. Можешь начать заново, если передумаешь 🙂"
    )
    await callback.answer()
