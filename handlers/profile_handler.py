from aiogram import Router, types
from database import get_pool

router = Router()

# -------------------------------
# 👤 Профиль пользователя
# -------------------------------
@router.message(lambda m: m.text == "👤 Профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    pool = await get_pool()

    async with pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT username, first_name, finished_habits, finished_challenges, total_stars
            FROM users
            WHERE user_id = $1
        """, user_id)

    if not user:
        await message.answer("❌ Пользователь не найден в базе данных.")
        return

    username = user["username"] or "—"
    first_name = user["first_name"] or "—"
    habits = user["finished_habits"] or 0
    challenges = user["finished_challenges"] or 0
    stars = user["total_stars"] or 0

    text = (
        f"👤 *Твой профиль*\n\n"
        f"📛 Имя: *{first_name}*\n"
        f"🪪 Username: @{username}\n\n"
        f"💪 Завершённых привычек: *{habits}*\n"
        f"🏆 Завершённых челленджей: *{challenges}*\n"
        f"🌟 Всего звёзд: *{stars}*\n\n"
        f"Продолжай в том же духе! 💥"
    )

    await message.answer(text, parse_mode="Markdown")
