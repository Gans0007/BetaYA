from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import html

from data.achievements_data import ALL_ACHIEVEMENTS
from core.database import get_pool
from services.achievements.achievements_service import get_category_progress

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


# -------------------------------
# 🏆 Достижения — категории
# -------------------------------
@router.callback_query(lambda c: c.data == "profile:achievements")
async def show_achievement_categories(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logging.info(f"[ACHIEVEMENTS] Пользователь {user_id} открыл категории достижений")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔥 Дисциплина",
                    callback_data="achievements:category:discipline"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🥊 Тело",
                    callback_data="achievements:category:body"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧠 Ум",
                    callback_data="achievements:category:mind"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👑 Статус",
                    callback_data="achievements:category:status"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Деньги",
                    callback_data="achievements:category:money"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_to_profile_menu"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "🏆 *Достижения*\n\nВыбери категорию:",
        parse_mode="Markdown",
        reply_markup=kb
    )

    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("achievements:category:"))
async def show_category_achievements(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    category = callback.data.split(":")[-1]

    logging.info(
        f"[ACHIEVEMENTS] Пользователь {user_id} открыл категорию {category}"
    )

    if category not in ALL_ACHIEVEMENTS:
        await callback.answer("Категория не найдена", show_alert=True)
        return

    pool = await get_pool()

    async with pool.acquire() as conn:

        stats = await conn.fetchrow("""
            SELECT current_streak, total_confirmed_days
            FROM user_stats
            WHERE user_id = $1
        """, user_id)

        current_streak = stats["current_streak"] if stats else 0
        total_confirmed = stats["total_confirmed_days"] if stats else 0

        rows = await conn.fetch("""
            SELECT achievement_code
            FROM user_achievements
            WHERE user_id = $1
        """, user_id)

        earned_codes = {row["achievement_code"] for row in rows}

        # 📊 Получаем общий прогресс по категории
        progress = await get_category_progress(
            conn,
            user_id,
            category
        )

    achievements_list = ALL_ACHIEVEMENTS[category]

    # Заголовок красивый
    category_titles = {
        "discipline": "🔥 Дисциплина",
        "body": "🥊 Тело",
        "mind": "🧠 Ум",
        "status": "👑 Статус",
        "money": "💰 Деньги",
    }

    header = category_titles.get(category, category.capitalize())

    text = (
        f"{header}\n\n"
        f"🏆 Выполнено: {progress['completed']} / {progress['total']}\n\n"
    )

    for achievement in achievements_list:

        code = achievement["code"]
        title = achievement["title"]
        description = achievement["description"]
        icon = achievement["icon"]
        condition_type = achievement["condition_type"]
        condition_value = achievement["condition_value"]

        if condition_type == "streak":
            progress_value = current_streak
        elif condition_type == "total_confirms":
            progress_value = total_confirmed
        else:
            progress_value = 0

        if code in earned_codes:
            status_icon = "✅"
            progress_text = "Получено"
        else:
            status_icon = "🔒"
            progress_text = f"{progress_value} / {condition_value}"

        safe_title = html.escape(str(title))
        safe_desc = html.escape(str(description))
        safe_progress = html.escape(str(progress_text))

        text += (
            f"{status_icon} {icon} <b>{safe_title}</b>\n"
            f"{safe_desc}\n"
            f"Прогресс: {safe_progress}\n\n"
        )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="profile:achievements"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb
    )

    await callback.answer()
