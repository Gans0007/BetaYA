from aiogram import Router, types
from database import get_pool
from handlers.confirm_habit_handler import get_habit_buttons

router = Router()

# -------------------------------
# 🔹 Активные задания (привычки + челленджи)
# -------------------------------
@router.message(lambda m: m.text == "📋 Активные задания")
async def show_active_tasks(message: types.Message):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, name, description, days, done_days, is_challenge
            FROM habits
            WHERE user_id = $1 AND is_active = TRUE
            ORDER BY is_challenge DESC, created_at DESC
        """, message.from_user.id)

    if not rows:
        await message.answer("😴 У тебя пока нет активных привычек или челленджей.")
        return

    for row in rows:
        name = row["name"]
        desc = row["description"]
        total_days = row["days"]
        done = row["done_days"]
        progress = int((done / total_days) * 100) if total_days > 0 else 0
        header = "🔥 Активный челлендж:" if row["is_challenge"] else "⚡️ Активная привычка:"

        text = (
            f"{header}\n\n"
            f"🏁 *Название:* {name}\n"
            f"📖 *Описание:* {desc}\n"
            f"📅 *Прогресс:* {done} из {total_days} дней ({progress}%)"
        )

        keyboard = await get_habit_buttons(row["id"], message.from_user.id)
        await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
