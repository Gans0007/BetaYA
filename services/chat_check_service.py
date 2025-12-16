from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

CHAT_ID = "@yourambitions_chat"  # или числовой ID

async def is_user_in_chat(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHAT_ID, user_id)
        return member.status not in ("left", "kicked")
    except TelegramBadRequest:
        return False
