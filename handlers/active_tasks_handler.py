from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_pool
from handlers.confirm_habit_handler import get_habit_buttons
import pytz

router = Router()


# ---------- helper: вывод карточки привычки ----------
async def send_habit_card(message: types.Message, habit, user_id: int):
    done, total = habit["done_days"], habit["days"]
    progress = int((done / total) * 100) if total > 0 else 0
    diff_text = {1: "⭐ Легко", 2: "⭐⭐ Средне", 3: "⭐⭐⭐ Сложно"}.get(habit["difficulty"], "⭐ Легко")

    if habit["last_date"]:
        tz = pytz.timezone(habit["timezone"] or "Europe/Kyiv")
        last_text = habit["last_date"].astimezone(tz).strftime("%d.%m.%Y %H:%M")
    else:
        last_text = "ещё не подтверждалась"

    header = "🔥 Активный челлендж:" if habit["is_challenge"] else "⚡️ Активная привычка:"

    text = (
        f"{header}\n\n"
        f"🏁 *Название:* {habit['name']}\n"
        f"📖 *Описание:* {habit['description']}\n"
        f"📅 *Прогресс:* {done} из {total} дней ({progress}%)\n"
        f"🎯 *Сложность:* {diff_text}\n"
        f"🕒 *Последнее подтверждение:* {last_text}"
    )

    keyboard = await get_habit_buttons(habit["id"], user_id)
    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)


# ---------- helper: строит текст и клаву списка ----------
async def build_active_list(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, name, is_challenge
            FROM habits
            WHERE user_id = $1 AND is_active = TRUE
            ORDER BY is_challenge DESC, created_at DESC
        """, user_id)

    if not rows:
        return None, None

    kb_rows = []
    for r in rows:
        title = f"🔥 {r['name']}" if r["is_challenge"] else r["name"]
        kb_rows.append([InlineKeyboardButton(text=title, callback_data=f"habit_{r['id']}")])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    text = ("📋 *Твои активные привычки и челленджи:*\n\n"
            "Нажми на любую, чтобы открыть карточку 👇")
    return text, kb, rows


# ---------- список активных: message-хендлер ----------
@router.message(lambda m: m.text == "📋 Активные задания")
async def show_active_tasks(message: types.Message):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT h.id, h.name, h.description, h.days, h.done_days, h.is_challenge, h.difficulty,
                   (SELECT datetime FROM confirmations WHERE habit_id = h.id ORDER BY datetime DESC LIMIT 1) AS last_date,
                   u.timezone
            FROM habits h
            JOIN users u ON u.user_id = h.user_id
            WHERE h.user_id = $1 AND h.is_active = TRUE
            ORDER BY h.is_challenge DESC, h.created_at DESC
        """, message.from_user.id)

    if not rows:
        await message.answer("😴 У тебя пока нет активных привычек или челленджей.")
        return

    # 🔹 если ≤ 2 привычек — показываем карточки сразу
    if len(rows) <= 2:
        for habit in rows:
            await send_habit_card(message, habit, message.from_user.id)
        return

    # 🔹 если > 2 — показываем меню
    text, kb, _ = await build_active_list(message.from_user.id)
    await message.answer(text, parse_mode="Markdown", reply_markup=kb)


# ---------- карточка привычки: callback-хендлер ----------
@router.callback_query(F.data.startswith("habit_"))
async def show_habit_card(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    pool = await get_pool()
    async with pool.acquire() as conn:
        habit = await conn.fetchrow("""
            SELECT h.id, h.name, h.description, h.days, h.done_days, h.is_challenge, h.difficulty,
                   (SELECT datetime FROM confirmations WHERE habit_id = h.id ORDER BY datetime DESC LIMIT 1) AS last_date,
                   u.timezone
            FROM habits h
            JOIN users u ON u.user_id = h.user_id
            WHERE h.id = $1 AND h.user_id = $2
        """, habit_id, user_id)

    if not habit:
        await callback.message.edit_text("❌ Привычка не найдена или уже завершена.")
        await callback.answer()
        return

    done, total = habit["done_days"], habit["days"]
    progress = int((done / total) * 100) if total > 0 else 0
    diff_text = {1: "⭐ Легко", 2: "⭐⭐ Средне", 3: "⭐⭐⭐ Сложно"}.get(habit["difficulty"], "⭐ Легко")

    if habit["last_date"]:
        tz = pytz.timezone(habit["timezone"] or "Europe/Kyiv")
        last_text = habit["last_date"].astimezone(tz).strftime("%d.%m.%Y %H:%M")
    else:
        last_text = "ещё не подтверждалась"

    header = "🔥 Активный челлендж:" if habit["is_challenge"] else "⚡️ Активная привычка:"

    text = (
        f"{header}\n\n"
        f"🏁 *Название:* {habit['name']}\n"
        f"📖 *Описание:* {habit['description']}\n"
        f"📅 *Прогресс:* {done} из {total} дней ({progress}%)\n"
        f"🎯 *Сложность:* {diff_text}\n"
        f"🕒 *Последнее подтверждение:* {last_text}"
    )

    keyboard = await get_habit_buttons(habit_id, user_id)
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="⬅ Назад к списку", callback_data="show_active_list")])

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()


# ---------- назад к списку: callback-хендлер ----------
@router.callback_query(F.data == "show_active_list")
async def back_to_active_list(callback: types.CallbackQuery):
    text, kb, rows = await build_active_list(callback.from_user.id)
    if not rows:
        await callback.message.edit_text("😴 У тебя пока нет активных привычек или челленджей.")
    else:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()
