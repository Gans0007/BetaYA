from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

async def check_subscription(bot: Bot, user_id: int, chat_id: str) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except TelegramBadRequest:
        return False
