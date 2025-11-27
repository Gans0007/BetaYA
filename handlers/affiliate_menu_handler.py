from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.affiliate_service import affiliate_service

router = Router()


# -------------------------------
# 💼 Меню партнёрки
# -------------------------------
@router.callback_query(lambda c: c.data == "affiliate_menu")
async def show_affiliate_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # получаем данные через сервис — не через репозиторий!
    dashboard = await affiliate_service.get_affiliate_dashboard(user_id)

    code = dashboard["code"]

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

    bot_username = (await callback.message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={code}"

    text = (
        "💼 *Партнёрка*\n\n"
        f"🔗 Твой реферальный код:\n`{code}`\n\n"
        f"👥 Приглашено всего: *{dashboard['invited']}*\n"
        f"🔥 Активных пользователей: *{dashboard['active']}*\n"
        f"💰 Заработано: *{dashboard['payments']}$*\n\n"
        "Распространяй эту ссылку:\n"
        f"{ref_link}\n\n"
        "Когда твои люди становятся *активными*,\n"
        "ты зарабатываешь деньги по договору с нами. 💰"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Мои рефералы", callback_data="affiliate_referrals_list")],
            [InlineKeyboardButton(text="💰 Выплаты", callback_data="affiliate_payments_list")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile_menu")]
        ]
    )

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()


# -------------------------------
# 👥 Список рефералов
# -------------------------------
@router.callback_query(lambda c: c.data == "affiliate_referrals_list")
async def show_affiliate_referrals(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    referrals = await affiliate_service.get_my_referrals(user_id)

    if not referrals:
        text = "У тебя пока нет рефералов 😔"
    else:
        text = "👥 *Твои рефералы:*\n\n"
        for r in referrals:
            status = "🟢 активен" if r["is_active"] else "🔴 не активен"
            text += f"@{r['username']} — {status}\n"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="affiliate_menu")]
        ]
    )

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()


# -------------------------------
# 💰 История выплат
# -------------------------------
@router.callback_query(lambda c: c.data == "affiliate_payments_list")
async def show_affiliate_payments(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    payments = await affiliate_service.get_affiliate_payments_list(user_id)

    if not payments:
        text = "Пока ещё не было активных рефералов 💸"
    else:
        text = "💰 *Зачисления:*\n\n"
        for p in payments:
            text += f"@{p['username']} активировался — ты получил выплату\n"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="affiliate_menu")]
        ]
    )

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()
