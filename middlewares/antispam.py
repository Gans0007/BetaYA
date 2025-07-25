from aiogram import BaseMiddleware
from datetime import datetime, timedelta
from typing import Callable, Awaitable, Dict, Any
from config import ADMIN_IDS  # импортируем список админов


class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, delay: int = 1):
        super().__init__()
        # задержка между действиями
        self.delay = timedelta(seconds=delay)
        # хранение времени последнего действия
        self.last_action: Dict[int, datetime] = {}

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event,
        data: Dict[str, Any]
    ):
        # Получаем user_id (работает и для callback, и для сообщений)
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        user_id = user.id

        # Исключение для администраторов
        if user_id in ADMIN_IDS:
            return await handler(event, data)

        now = datetime.now()

        # Проверка задержки
        last_time = self.last_action.get(user_id)
        if last_time and now - last_time < self.delay:
            # Если пользователь кликает слишком быстро
            if hasattr(event, "answer"):
                await event.answer("⏳ Слишком быстро, подожди немного.")
            return  # просто игнорируем

        # Обновляем время последнего действия
        self.last_action[user_id] = now

        return await handler(event, data)
