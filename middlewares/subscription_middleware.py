# middlewares/subscription_middleware.py

from aiogram import BaseMiddleware
import logging

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        """
        Обновлённый middleware.

        Больше НЕ блокирует действия пользователя.
        Подписочная логика теперь проверяется
        только в конкретных местах (добавление привычек).

        Middleware оставлен как точка расширения,
        если в будущем понадобится централизованная логика.
        """
        return await handler(event, data)
