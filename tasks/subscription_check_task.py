import asyncio
from datetime import datetime, timezone, timedelta

from aiogram import types
from config import PUBLIC_CHANNEL_ID
from core.database import get_pool

from repositories.affiliate_repository import get_affiliate_for_user
from services.affiliate_service import affiliate_service

from core.shutdown import shutdown_event

import logging
logger = logging.getLogger(__name__)


async def subscription_checker(bot):

    pool = await get_pool()

    while not shutdown_event.is_set():
        now = datetime.now(timezone.utc)

        async with pool.acquire() as conn:
            users = await conn.fetch("""
                SELECT user_id,
                       has_access,
                       access_until,
                       subscription_notified
                FROM users
            """)

            for u in users:
                user_id = u["user_id"]
                has_access = u["has_access"]
                access_until = u["access_until"]
                notified = u["subscription_notified"]

                # -------------------------------------------------
                # ✅ 1. Подписка активна — ничего не делаем
                # -------------------------------------------------
                if has_access and access_until and access_until > now:
                    continue

                # -------------------------------------------------
                # 🔍 2. Проверяем, состоит ли пользователь в канале
                # -------------------------------------------------
                try:
                    member = await bot.get_chat_member(PUBLIC_CHANNEL_ID, user_id)
                    in_channel = member.status in ("member", "administrator", "creator")
                except Exception:
                    in_channel = False

                # -------------------------------------------------
                # 🟢 3. Пользователь В КАНАЛЕ → авто-продление
                # -------------------------------------------------
                if in_channel:
                    new_until = now + timedelta(days=30)

                    await conn.execute("""
                        UPDATE users
                        SET has_access = TRUE,
                            access_until = $2,
                            subscription_notified = FALSE
                        WHERE user_id = $1
                    """, user_id, new_until)

                    # 💸 Начисление партнёру по УРОВНЮ (автопродление)
                    SUBSCRIPTION_PRICE = 10.0

                    ok, amount, level = await affiliate_service.reward_for_subscription_payment(
                        referral_user_id=user_id,
                        subscription_price=SUBSCRIPTION_PRICE
                    )

                    if ok and amount > 0 and level:
                        affiliate_id = await get_affiliate_for_user(user_id)

                        logger.info(
                            f"[REF-RENEW] Пользователь {user_id} → affiliate {affiliate_id}: "
                            f"{level['title']} ({level['percent']}%) → ${amount}"
                        )

                        try:
                            await bot.send_message(
                                affiliate_id,
                                f"🔥 Реферал продлил подписку автоматически!\n"
                                f"🏅 Уровень партнёра: {level['emoji']} {level['title']} ({level['percent']}%)\n"
                                f"💰 Начислено: ${amount}"
                            )
                        except Exception as e:
                            logger.warning(
                                f"[REF-NOTIFY-FAILED] Affiliate {affiliate_id}: {e}"
                            )

                    continue

                # -------------------------------------------------
                # 🔴 4. Подписка реально истекла (по access_until)
                # -------------------------------------------------
                subscription_expired = not access_until or access_until <= now

                if subscription_expired and not notified:
                    # 🔒 Отключаем доступ ОДИН РАЗ
                    await conn.execute("""
                        UPDATE users
                        SET has_access = FALSE,
                            subscription_notified = TRUE
                        WHERE user_id = $1
                    """, user_id)
                    # 🚪 Удаляем пользователя из закрытого чата
                    try:
                        await bot.ban_chat_member(
                            chat_id=-1002392347850,
                            user_id=user_id
                        )
                        await bot.unban_chat_member(
                            chat_id=-1002392347850,
                            user_id=user_id
                        )
                        logger.info(
                            f"[CHAT-REMOVE] Пользователь {user_id} удалён из закрытого чата"
                        )
                    except Exception as e:
                        logger.warning(
                            f"[CHAT-REMOVE-ERROR] Пользователь {user_id}: {e}"
                        )


                    # ❌ Деактивируем реферала ОДИН РАЗ
                    try:
                        await affiliate_service.deactivate_referral(user_id)
                        logger.info(
                            f"[REF-DEACTIVATE] Пользователь {user_id} → подписка закончилась"
                        )
                    except Exception as e:
                        logger.error(
                            f"[REF-DEACTIVATE-ERROR] Пользователь {user_id}: {e}"
                        )

                    # 📩 Уведомляем пользователя ОДИН РАЗ
                    try:
                        await bot.send_message(
                            user_id,
                            "⛔ *Подписка закончилась!*\n\n"
                            "Чтобы продолжить пользоваться преймуществами PRO версии — оплати доступ.\n\n"
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
                        logger.warning(
                            f"[USER-NOTIFY-FAILED] Пользователь {user_id}: {e}"
                        )

                # -------------------------------------------------
                # 🟡 5. Уже уведомлён → НИЧЕГО НЕ ДЕЛАЕМ
                # -------------------------------------------------
                # никаких логов
                # никаких сообщений
                # никаких деактиваций

        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=600)
        except asyncio.TimeoutError:
            pass
