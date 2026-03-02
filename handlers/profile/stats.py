#handlers/profile/stats
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
    await callback.answer()

    result = await profile_stats_service.process_level_up_request(user_id)

    # Максимальная лига
    if not result.get("next_league"):
        await callback.message.answer("🔥 Ты уже достиг максимальной лиги.")
        return

    # Условия НЕ выполнены → просто пишем сколько не хватает
    if not result.get("can_level_up"):
        await callback.message.answer(
            f"❌ Для повышения уровня не хватает:\n\n"
            f"⭐ {result['need_stars']} звёзд\n"
            f"✨ {result['need_xp']} XP"
        )
        return

    # Условия выполнены → переносим
    next_l = result["next_league"]

    await profile_stats_service.apply_level_up(
        user_id,
        next_l["name"],
        next_l["emoji"]
    )

    await callback.message.answer(
        f"🏆 Повышение!\n\n"
        f"Ты перешёл в лигу {next_l['emoji']} {next_l['name']}!\n\n"
        f"«{next_l['quote']}»"
    )
