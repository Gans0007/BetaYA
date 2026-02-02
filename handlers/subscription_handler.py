from aiogram import Router, types
from database import get_pool
from datetime import datetime, timedelta, timezone
from config import PUBLIC_CHANNEL_ID
from repositories.affiliate_repository import (
    get_affiliate_for_user,
    mark_referral_inactive
)

from services.affiliate_service import affiliate_service

import logging

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

# 🔄 Проверка подписки (кнопка "Проверить доступ")
@router.callback_query(lambda c: c.data == "subscription_check")
async def check_subscription_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logging.info(f"[NEED TO PAY] Пользователь {user_id} нажал 'Проверить доступ'")

    # 1️⃣ Проверяем вступление в приватную группу
    try:
        member = await callback.message.bot.get_chat_member(PUBLIC_CHANNEL_ID, user_id)
        in_group = member.status in ("member", "administrator", "creator")
    except Exception:
        in_group = False

    pool = await get_pool()

    # 2️⃣ Если пользователь в канале → активируем подписку на 30 дней
    if in_group:
        now = datetime.now(timezone.utc)

        # 🛡 Защита от двойного нажатия / повторного начисления
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT access_until
                FROM users
                WHERE user_id = $1
            """, user_id)

        if row and row["access_until"] and row["access_until"] > now:
            logging.info(
                f"[NEED TO PAY] Повторное нажатие 'Проверить доступ' "
                f"для пользователя {user_id} — подписка уже активна"
            )

            await callback.message.edit_text(
                f"✅ Подписка уже активна!\n"
                f"Доступ до: <b>{row['access_until'].strftime('%d.%m.%Y')}</b>",
                parse_mode="HTML"
            )
            await callback.answer()
            return

        # ⏳ Подписка истекла → продлеваем
        new_until = now + timedelta(days=30)

        logging.info(
            f"[NEED TO PAY] Подписка подтверждена — доступ до {new_until} "
            f"для пользователя {user_id}"
        )

        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE users
                SET has_access = TRUE,
                    access_until = $2
                WHERE user_id = $1
            """, user_id, new_until)

        # 💸 Начисление партнёру по УРОВНЮ (первый платёж / продление)
        SUBSCRIPTION_PRICE = 10.0

        ok, amount, level = await affiliate_service.reward_for_subscription_payment(
            referral_user_id=user_id,
            subscription_price=SUBSCRIPTION_PRICE
        )

        if ok and amount > 0 and level:
            affiliate_id = await get_affiliate_for_user(user_id)

            logging.info(
                f"[NEED TO PAY] Начисление партнёру {affiliate_id}: "
                f"{level['title']} ({level['percent']}%) → ${amount}"
            )

            try:
                await callback.message.bot.send_message(
                    affiliate_id,
                    f"🔥 Реферал оплатил подписку!\n"
                    f"🏅 Уровень партнёра: {level['emoji']} {level['title']} ({level['percent']}%)\n"
                    f"💰 Начислено: ${amount}"
                )
            except Exception as e:
                logging.warning(
                    f"[NEED TO PAY] Не удалось отправить уведомление партнёру {affiliate_id}: {e}"
                )

        await callback.message.edit_text(
            f"✅ Подписка подтверждена!\n"
            f"Доступ активен до: <b>{new_until.strftime('%d.%m.%Y')}</b>\n\n"
            "Приятного пользования ботом 🔥",
            parse_mode="HTML"
        )

        await callback.answer()
        return


    # 3️⃣ Если пользователь НЕ в канале → подписка не активна
    logging.info(f"[NEED TO PAY] Подписка НЕ найдена у пользователя {user_id} — требуется оплата")

    try:
        await mark_referral_inactive(user_id)
    except:
        pass

    await callback.message.answer(
        "⛔ Подписка не найдена.\n\n"
        "Чтобы продолжить пользоваться ботом — оплати подписку:",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="💳 Перейти к оплате",
                        url="https://t.me/tribute/app?startapp=ssdz"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="🔎 Проверить снова",
                        callback_data="subscription_check"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()
