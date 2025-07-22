from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo, InputMediaPhoto
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == "rules_examples")
async def handle_rules_examples(callback: CallbackQuery, bot: Bot):
    await callback.answer()

    text = (
        "📜 <b>Примеры контента для соцсетей</b>, чтобы получить награду в USDT:\n\n"
        "🎥 Видео 1 — любое видео с канала: t.me/yourambitions с отметкой канала \n"
        "📱 Фото 2 — Фото или видео с выполненой карточкой привычки или ссылкой на канал или бота: \n https://t.me/LiteVAmbitionBot \n"
        "🧠 Видео 3 — Разговорное видео \n\n"
        "⚠️ <b>Контент должен быть полезен и выполнен с намерением</b>.\n Главное условие наличия ссылки или карточки привычки. Креатив приветствуется \n И помни за активных друзей тоже начисляются usdt \n"
        "Ты выкладываешь в соцсети, мы оцениваем — и начисляем 💸 USDT."
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monetization_rules")]
    ])

    await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")

    media_group = [
        InputMediaVideo(
            media="BAACAgIAAxkBAAKRPmh_SsEsJkThX7mFBcdcndcMtzLEAAI8dwACsPP4S7dOhlgcknMlNgQ",
            caption="🎥 Пример: видео взято с канала ТВОИ АМБИЦИИ (инст)"
        ),
        InputMediaPhoto(
            media="AgACAgIAAxkBAAKRh2h_U8O1YiyD4xXKdfXPz1MPn7XKAAI08DEbsPP4S5XhHK8NBT4RAQADAgADeQADNgQ",
            caption="🏃‍ Пример: фотография с выполненой карточкой привычки и ссылкой"
        ),
        InputMediaVideo(
            media="BAACAgIAAxkBAAKRo2h_VelT9OY-JQaLdXRt-yoPAicjAALNdwACsPP4S6M-PNefNj7GNgQ",
            caption="📚 Пример: разговорное видео с карточкой привычки"
        ),
    ]

    try:
        await bot.send_media_group(chat_id=callback.from_user.id, media=media_group)
    except Exception as e:
        logger.error(f"[EXAMPLES] ❌ Ошибка при отправке медиагруппы: {e}")
        await callback.message.answer("⚠️ Видео-примеры временно недоступны.")
