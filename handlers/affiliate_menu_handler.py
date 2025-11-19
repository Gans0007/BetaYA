from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from repositories.affiliate_repository import (
    get_affiliate_stats,
    get_referral_code,
    get_payments
)

router = Router()

# -------------------------------
# 💼 Меню партнёрки
# -------------------------------
@router.callback_query(lambda c: c.data == "affiliate_menu")
async def show_affiliate_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # статистика
    stats = await get_affiliate_stats(user_id)
    code = await get_referral_code(user_id)

    # если нет партнёрки
    if not code:
        text = (
            "💼 *Партнёрка*\n\n"
            "Пока у тебя не задан реферальный код.\n"
            "Напиши админу, чтобы он выдал тебе партнёрку."
        )
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile_menu")]
            ]
        )
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
        await callback.answer()
        return

    # ссылка
    bot_username = (await callback.message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={code}"

    # 💰 получаем выплаты
    payments = await get_payments(user_id)

    text = (
        "💼 *Партнёрка*\n\n"
        f"🔗 Твой реферальный код:\n`{code}`\n\n"
        f"👥 Приглашено всего: *{stats['invited']}*\n"
        f"🔥 Активных пользователей: *{stats['active']}*\n"
        f"💰 Заработано: *{payments}$*\n\n"
        "Распространяй эту ссылку:\n"
        f"{ref_link}\n\n"
        "Когда твои люди становятся *активными*,\n"
        "ты зарабатываешь деньги по договору с нами. 💰"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile_menu")]
        ]
    )

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()
