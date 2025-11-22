import asyncio
from datetime import datetime, timezone, timedelta
from aiogram import Bot, types
from config import BOT_TOKEN, PUBLIC_CHANNEL_ID
from database import get_pool
from repositories.affiliate_repository import get_affiliate_for_user, add_payment_to_affiliate


async def subscription_checker():
    """
    Каждые 10 минут:
    - Проверяет срок подписки пользователя
    - Если он в платной группе → продлевает подписку на 30 дней
    - Если нет → отключает и отправляет уведомление
    - При каждом продлении начисляет партнёру $0.50
    """

    bot = Bot(token=BOT_TOKEN)

    while True:
        pool = await get_pool()
        now = datetime.now(timezone.utc)

        async with pool.acquire() as conn:
            users = await conn.fetch("""
                SELECT user_id, has_access, access_until
                FROM users
            """)

        for u in users:
            user_id = u["user_id"]
            has_access = u["has_access"]
            access_until = u["access_until"]

            # подписка ещё действует
            if has_access and access_until and access_until > now:
                continue

            # проверяем участие в канале
            try:
                member = await bot.get_chat_member(PUBLIC_CHANNEL_ID, user_id)
                in_group = member.status in ("member", "administrator", "creator")
            except Exception:
                in_group = False

            # 1️⃣ Если пользователь в канале → продлеваем подписку на 30 дней
            if in_group:
                new_until = now + timedelta(days=30)

                async with pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE users
                        SET has_access = TRUE,
                            access_until = $2
                        WHERE user_id = $1
                    """, user_id, new_until)

                # 💸 Начисление партнёру $0.50
                affiliate_id = await get_affiliate_for_user(user_id)

                if affiliate_id:
                    await add_payment_to_affiliate(affiliate_id, 0.50)

                    try:
                        await bot.send_message(
                            affiliate_id,
                            "🔥 Твой реферал продлил подписку (автоматически)!\n💰 Тебе начислено $0.50"
                        )
                    except:
                        pass

                continue  # очень важно!

            # 2️⃣ Если пользователь НЕ в канале → отключаем доступ
            if not has_access or (access_until and access_until <= now):

                async with pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE users
                        SET has_access = FALSE
                        WHERE user_id = $1
                    """, user_id)

                # уведомление пользователю
                try:
                    await bot.send_message(
                        user_id,
                        "⛔ *Подписка закончилась!*\n\n"
                        "Чтобы продолжить пользоваться ботом — оплати доступ.\n\n"
                        "Выбери действие ниже:",
                        parse_mode="Markdown",
                        reply_markup=types.InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    types.InlineKeyboardButton(
                                        text="💳 Оплатить подписку",
                                        url="https://t.me/tribute/app?startapp=ssdz"
                                    )
                                ],
                                [
                                    types.InlineKeyboardButton(
                                        text="🔎 Проверить доступ",
                                        callback_data="subscription_check"
                                    )
                                ]
                            ]
                        )
                    )
                except:
                    pass

        await asyncio.sleep(600)
