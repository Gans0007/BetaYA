import asyncio
from aiogram.types import Message

async def safe_replace_message(message: Message, text: str, reply_markup=None, delay: float = 0.4, parse_mode: str = None):
    try:
        await message.delete()
        await asyncio.sleep(delay)
    except Exception:
        pass
    await message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)

async def try_edit_message(callback, text=None, markup=None):
    try:
        if text:
            await callback.message.edit_text(text, reply_markup=markup)
        elif markup:
            await callback.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass
