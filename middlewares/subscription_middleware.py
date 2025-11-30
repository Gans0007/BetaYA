from aiogram import BaseMiddleware, types
from datetime import datetime, timezone
from database import get_pool


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        
        # --- Разрешённые действия даже при блокировке ---
        
        # Разрешаем /start
        if isinstance(event, types.Message):
            if event.text == "/start":
                return await handler(event, data)

        # Разрешаем текстовую кнопку "Оплатить / Проверить"
        if isinstance(event, types.Message):
            if event.text == "💳 Оплатить подписку / Проверить":
                return await handler(event, data)

        # Разрешаем callback-кнопку "subscription_check"
        if isinstance(event, types.CallbackQuery):
            if event.data == "subscription_check":
                return await handler(event, data)


        # --- Общая логика блокировки ---

        user_id = event.from_user.id

        pool = await get_pool()
        async with pool.acquire() as conn:
            user = await conn.fetchrow("""
                SELECT total_confirmed_days, has_access, access_until
                FROM users
                WHERE user_id=$1
            """, user_id)

        # ===========================================
        # 🔥 ЕСЛИ ПОЛЬЗОВАТЕЛЯ НЕТ — АВТОЗАПУСК /start
        # ===========================================
        if not user:
             return await handler(event, data)
            

        total_days = user["total_confirmed_days"]
        has_access = user["has_access"]
        access_until = user["access_until"]

        now = datetime.now(timezone.utc)

        # Условия блокировки
        need_block = (
            total_days >= 7 and (
                not has_access or
                not access_until or
                access_until < now
            )
        )

        if need_block:

            # --- Вертикальные кнопки ---
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="💳 Оплатить подписку",
                            url="https://t.me/tribute/app?startapp=ssdz"   # ← ВСТАВЬ СВОЮ ССЫЛКУ
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

            # Если это message
            if isinstance(event, types.Message):
                await event.answer(
                    text,
                    reply_markup=kb,
                    parse_mode="HTML"
                )
                return

            # Если это callback
            if isinstance(event, types.CallbackQuery):
                await event.message.edit_text(
                    text,
                    reply_markup=kb,
                    parse_mode="HTML"
                )
                await event.answer()
                return

        # Если нет блокировки — значит подписка активна
        # это случается и при автоматическом продлении
        try:
            # Проверяем — является ли пользователь чьим-то рефералом
            from repositories.affiliate_repository import get_affiliate_for_user
            from services.affiliate_service import affiliate_service

            affiliate_id = await get_affiliate_for_user(user_id)

            if affiliate_id and has_access and access_until >= now:
                # Пробуем активировать реферальную подписку
                await affiliate_service.activate_referral(user_id, 0.50)

        except Exception as e:
            print(f"[AUTO_SUBSCRIPTION ERROR] {e}")

        # Пропускаем дальше
        return await handler(event, data)

