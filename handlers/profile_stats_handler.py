from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging

from services.profile_stats_service import profile_stats_service

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


@router.callback_query(lambda c: c.data == "profile_stats")
async def show_stats(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logging.info(f"[STATISTIC] Пользователь {user_id} открыл статистику")
    await callback.answer()

    text = await profile_stats_service.build_stats_text(user_id)

    if not text:
        logging.warning(f"[STATISTIC] Не удалось получить статистику для пользователя {user_id}")
        await callback.message.edit_text("❌ Пользователь не найден.")
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Level Up", callback_data="next_league")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile_menu")]
        ]
    )

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(lambda c: c.data == "next_league")
async def process_level_up(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logging.info(f"[STATISTIC] Пользователь {user_id} нажал Level Up")
    await callback.answer()

    result = await profile_stats_service.process_level_up_request(user_id)

    if not result["next_league"]:
        logging.info(f"[STATISTIC] Пользователь {user_id} уже достиг максимальной лиги")
        await callback.message.edit_text("🔥 Ты уже достиг максимальной лиги!")
        return

    if not result["can_level_up"]:
        need_stars = result["need_stars"]
        need_xp = result["need_xp"]

        logging.info(f"[STATISTIC] Пользователю {user_id} не хватает {need_stars}⭐ и {need_xp} XP до повышения")

        conf_count = await profile_stats_service.get_weekly_confirmation_rate(user_id)

        if not conf_count:
            estimate = "Сделай хотя бы одно подтверждение 💪"
        else:
            avg_xp = float((conf_count * 1.4) / 7)
            days = float(need_xp) / avg_xp if avg_xp > 0 else 999
            low = max(1, int(days * 0.85))
            high = max(1, int(days * 1.15))
            estimate = f"~ {low}–{high} дней 🔥"

        await callback.message.answer(
            f"⏳ До новой лиги:\n"
            f"{estimate}\n\n"
            f"⭐ Ост осталось: {need_stars}⭐\n"
            f"✨ Осталось: {need_xp} XP",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="profile_stats")]]
            )
        )
        return

    # МОЖНО ПОВЫСИТЬ ЛИГУ
    next_l = result["next_league"]
    logging.info(f"[STATISTIC] Пользователь {user_id} повышен до: {next_l['emoji']} {next_l['name']}")

    await profile_stats_service.apply_level_up(user_id, next_l["name"], next_l["emoji"])

    await callback.message.answer(
        f"🏆 Новая лига!\n"
        f"Ты поднялся до уровня: {next_l['emoji']} {next_l['name']}\n\n"
        f"«{next_l['quote']}»\n"
        f"Продолжай в том же духе 🚀"
    )
