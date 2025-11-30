import asyncio
from datetime import datetime, timezone, timedelta
from aiogram import Bot, types
from config import BOT_TOKEN, PUBLIC_CHANNEL_ID
from database import get_pool
from repositories.affiliate_repository import get_affiliate_for_user
from services.affiliate_service import affiliate_service

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

async def subscription_checker():

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

                if has_access and access_until and access_until > now:
                    continue

                try:
                    member = await bot.get_chat_member(PUBLIC_CHANNEL_ID, user_id)
                    in_group = member.status in ("member", "administrator", "creator")
                except Exception:
                    in_group = False

                if in_group:
                    new_until = now + timedelta(days=30)

                    await conn.execute("""
                        UPDATE users
                        SET has_access = TRUE,
                            access_until = $2
                        WHERE user_id = $1
                    """, user_id, new_until)

                    affiliate_id = await get_affiliate_for_user(user_id)

                    if affiliate_id:
                        logging.info(f"[REF-ACTIVATE] Пользователь {user_id} → активирован системой авто-подписки → affiliate {affiliate_id}")
                        await affiliate_service.activate_referral(user_id, 0.50)

                        try:
                            await bot.send_message(
                                affiliate_id,
                                "🔥 Твой реферал продлил подписку (автоматически)!\n💰 Тебе начислено $0.50"
                            )
                        except Exception as e:
                            logging.warning(f"[REF-NOTIFY-FAILED] Не удалось отправить сообщение партнёру {affiliate_id} — {e}")

                    continue

                if not has_access or (access_until and access_until <= now):
                    await conn.execute("""
                        UPDATE users
                        SET has_access = FALSE
                        WHERE user_id = $1
                    """, user_id)

                    try:
                        await affiliate_service.deactivate_referral(user_id)
                        logging.info(f"[REF-DEACTIVATE] Пользователь {user_id} → не продлил подписку")
                    except Exception as e:
                        logging.error(f"[REF-DEACTIVATE-ERROR] Пользователь {user_id} — {e}")

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
                    except Exception as e:
                        logging.warning(f"[USER-NOTIFY-FAILED] Не удалось отправить сообщение пользователю {user_id} — {e}")

        await asyncio.sleep(600)

