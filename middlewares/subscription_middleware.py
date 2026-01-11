from aiogram import BaseMiddleware, types
from datetime import datetime, timezone
from database import get_pool
import logging

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):

        # ===============================
        # 🔓 Разрешённые действия всегда
        # ===============================

        if isinstance(event, types.Message):
            if event.text in ("/start", "💳 Оплатить подписку / Проверить"):
                return await handler(event, data)

        if isinstance(event, types.CallbackQuery):
            if event.data == "subscription_check":
                return await handler(event, data)

        # ===============================
        # 🔒 Основная логика блокировки
        # ===============================

        user_id = event.from_user.id
        now = datetime.now(timezone.utc)

        pool = await get_pool()
        async with pool.acquire() as conn:
            user = await conn.fetchrow("""
                SELECT total_confirmed_days, has_access, access_until
                FROM users
                WHERE user_id = $1
            """, user_id)

        # Если пользователя нет в БД — не блокируем
        if not user:
            return await handler(event, data)

        total_days = user["total_confirmed_days"]
        has_access = user["has_access"]
        access_until = user["access_until"]

        need_block = (
            total_days >= 10 and (
                not has_access or
                not access_until or
                access_until < now
            )
        )

        if need_block:
            kb = types.InlineKeyboardMarkup(
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

            text = (
                "⛔ <b>Бесплатные 7 активных дней закончились.</b>\n\n"
                "Чтобы продолжить пользоваться ботом — активируй подписку.\n\n"
                "Выбери действие ниже:"
            )

            if isinstance(event, types.Message):
                await event.answer(text, reply_markup=kb, parse_mode="HTML")
                return

            if isinstance(event, types.CallbackQuery):
                await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
                await event.answer()
                return

        # ✅ Если блокировки нет — просто пропускаем дальше
        return await handler(event, data)
