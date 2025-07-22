# handlers/referral_handler.py

from aiogram import Router, types, F
from aiogram import Bot  # добавь эту строку
from keyboards.monetization import get_referral_keyboard
from repositories.users.user_repo import get_confirmed_count
from config import REFERRAL_BANNER_PATH, REFERRAL_BASE_URL
import os

router = Router()

@router.callback_query(F.data == "monetization_referral")
async def show_referral_info(callback: types.CallbackQuery, bot: Bot, db):
    user_id = callback.from_user.id

    # Получаем всех рефералов
    query = """
        SELECT invited_id, is_active 
        FROM referrals 
        WHERE referrer_id = :referrer_id
    """
    rows = await db.fetch_all(query, {"referrer_id": user_id})
    referrals = [(row["invited_id"], row["is_active"]) for row in rows]

    total_referrals = len(referrals)
    active_referrals = sum(1 for _, is_active in referrals if is_active)

    # Формируем список активных друзей
    active_friends = []
    for invited_id, is_active in referrals:
        if is_active:
            try:
                user = await bot.get_chat(invited_id)
                name = user.full_name
                username = f"(@{user.username})" if user.username else ""
                active_friends.append(f"• {name} {username}")
            except Exception as e:
                active_friends.append(f"• Пользователь {invited_id}")

    referral_link = f"{REFERRAL_BASE_URL}?start={user_id}"

    # Базовый текст
    caption = (
        "<b>👥 Твоя реферальная программа</b>\n\n"
        f"🔗 <b>Ссылка:</b> {referral_link}\n\n"
        f"📊 Всего приглашено: <b>{total_referrals}</b>\n"
        f"🔥 Активных: <b>{active_referrals}</b>"
    )

    # Добавляем блок с именами активных друзей
    if active_friends:
        caption += "\n\n<b>✅ Активные друзья:</b>\n" + "\n".join(active_friends)

    caption += "\n\n🤑 Приглашай друзей и получай бонусы за активность!"

    await callback.message.edit_media(
        media=types.InputMediaPhoto(
            media=types.FSInputFile(REFERRAL_BANNER_PATH),
            caption=caption,
            parse_mode="HTML"
        ),
        reply_markup=get_referral_keyboard(referral_link)
    )
