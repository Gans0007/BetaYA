# handlers/monetization/balance_handler.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.formatting import as_list, as_marked_section, Bold
from services.monetization.balance_service import get_user_balance_and_history
from keyboards.monetization import get_balance_keyboard
from utils.ui import safe_replace_message

router = Router()

@router.callback_query(F.data == "balance")
async def show_balance(callback: CallbackQuery):
    user_id = callback.from_user.id
    usdt, xp, history = await get_user_balance_and_history(user_id)

    history_lines = [
        f"• +{entry['amount']} {entry['type'].upper()} — {entry['reason']} ({entry['date']})"
        for entry in history
    ]
    history_text = "\n".join(history_lines) if history_lines else "Нет начислений пока."

    text = (
        f"💰 <b>Твой баланс</b>\n\n"
        f"🪙 USDT: <b>{usdt:.2f}</b>\n"
        f"⭐ XP: <b>{xp}</b>\n\n"
        f"🧾 История начислений:\n{history_text}"
    )

    keyboard = get_balance_keyboard(show_withdraw=usdt >= 5)

    await safe_replace_message(callback.message, text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()
