from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

from services.affiliate_service import affiliate_service

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

# -------------------------------------------------
# 🧩 Утилита — красиво показывать имя пользователя
# -------------------------------------------------
def format_user(row):
    username = row.get("username")
    nickname = row.get("nickname")
    user_id = row.get("user_id")

    if username:
        return f"@{username}"
    if nickname:
        return f"{nickname}"
    return f"ID:{user_id}"


# -------------------------------------------------
# 💼 Меню партнёрки
# -------------------------------------------------
@router.callback_query(lambda c: c.data == "affiliate_menu")
async def show_affiliate_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logging.info(f"[AFFILIATE] Пользователь {user_id} открыл меню партнёрки")

    dashboard = await affiliate_service.get_affiliate_dashboard(user_id)
    code = dashboard["code"]

    bot_username = (await callback.message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={code}"

    text = (
        "💼 Партнёрская программа\n\n"
        f"🔗 Твой реферальный код: {code}\n"
        f"🌐 Реферальная ссылка:\n{ref_link}\n\n"
        f"👥 Всего приглашено: {dashboard['invited']}\n"
        f"🔥 Активных: {dashboard['active']}\n\n"
        f"💰 Заработано: {dashboard['payments']}$\n"
        f"🏦 Выплачено: {dashboard['paid_out']}$\n\n"
        "Ты получаешь 20% от стоимости подписки за каждого активного реферала."
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Мои рефералы", callback_data="affiliate_referrals_list")],
            [InlineKeyboardButton(text="💰 Выплаты", callback_data="affiliate_payments_list")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile_menu")]
        ]
    )

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


# -------------------------------------------------
# 👥 Список рефералов
# -------------------------------------------------
@router.callback_query(lambda c: c.data == "affiliate_referrals_list")
async def show_affiliate_referrals(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logging.info(f"[AFFILIATE] Пользователь {user_id} смотрит список рефералов")

    referrals = await affiliate_service.get_my_referrals(user_id)

    if not referrals:
        text = "😔 У тебя пока нет рефералов."
    else:
        text = "👥 Твои рефералы:\n\n"
        for r in referrals:
            name = format_user(r)
            status = "🟢 активен" if r["is_active"] else "🔴 не активен"
            text += f"{name} — {status}\n"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="affiliate_menu")]
        ]
    )

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


# -------------------------------------------------
# 💰 История выплат
# -------------------------------------------------
@router.callback_query(lambda c: c.data == "affiliate_payments_list")
async def show_affiliate_payments(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logging.info(f"[AFFILIATE] Пользователь {user_id} смотрит выплаты")

    payments = await affiliate_service.get_affiliate_payments_list(user_id)

    if not payments:
        text = "💸 Пока ещё не было активных рефералов."
    else:
        text = "💰 Выплаты:\n\n"
        for p in payments:
            name = format_user(p)
            amount = p.get("amount", "?")
            created_at = p.get("created_at")

            date_text = created_at.strftime("%d.%m.%Y") if created_at else ""

            text += f"• {name} → +{amount}$ ({date_text})\n"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="affiliate_menu")]
        ]
    )

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()
