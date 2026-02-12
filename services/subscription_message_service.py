# services/subscription_message_service.py

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💳 Оформить подписку",
                url="https://t.me/tribute/app?startapp=ssdz"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔄 Проверить доступ",
                callback_data="subscription_check"
            )
        ]
    ])
    return keyboard


async def show_subscription_limit_message(message: types.Message, active_count: int):
    text = (
        "🚀 <b>Бесплатный лимит достигнут</b>\n\n"
        f"Сейчас у тебя {active_count} активных привычек.\n"
        "В бесплатной версии доступно только 2.\n\n"
        "🔥 Хочешь добавлять без ограничений?\n"
        "Подключи PRO-доступ и прокачивай себя без лимитов."
    )

    await message.answer(
        text,
        reply_markup=get_subscription_keyboard(),
        parse_mode="HTML"
    )
