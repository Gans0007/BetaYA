from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_pool

router = Router()


# -------------------------------
# 📊 Статистика (бывший профиль)
# -------------------------------
@router.callback_query(lambda c: c.data == "profile_stats")
async def show_stats(callback: types.CallbackQuery):
    """Показывает статистику пользователя"""
    user_id = callback.from_user.id
    pool = await get_pool()

    async with pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT username, nickname, finished_habits, finished_challenges, 
                   total_stars, total_confirmed_days, joined_at
            FROM users
            WHERE user_id = $1
        """, user_id)

    if not user:
        await callback.message.edit_text("❌ Пользователь не найден в базе данных.")
        await callback.answer()
        return

    nickname = user["nickname"] or "—"
    if nickname.startswith("@"):  # 👈 убираем @, если он есть
        nickname = nickname[1:]

    habits = user["finished_habits"] or 0
    challenges = user["finished_challenges"] or 0
    stars = user["total_stars"] or 0
    confirmed_days = user["total_confirmed_days"] or 0
    joined_at = user["joined_at"].strftime("%d.%m.%Y") if user["joined_at"] else "—"

    text = (
        f"📊 *Твоя статистика*\n\n"
        f"🪪 Nickname: *{nickname}*\n"
        f"📅 Дата вступления: *{joined_at}*\n\n"
        f"💪 Завершённых привычек: *{habits}*\n"
        f"🏆 Завершённых челленджей: *{challenges}*\n"
        f"🌟 Всего звёзд: *{stars}*\n"
        f"📅 Всего подтверждённых дней: *{confirmed_days}*\n\n"
        f"Продолжай в том же духе! 💥"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile_menu")]
        ]
    )

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()
