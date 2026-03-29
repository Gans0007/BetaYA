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
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile_menu")]
        ]
    )

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
