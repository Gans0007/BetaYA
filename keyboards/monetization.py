from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_balance_keyboard(show_withdraw: bool = False) -> InlineKeyboardMarkup:
    buttons = []

    if show_withdraw:
        buttons.append(
            InlineKeyboardButton(
                text="💸 Вывести USDT",
                url="https://t.me/ssprvz01"
            )
        )

    buttons.append(
        InlineKeyboardButton(text="◀️ Назад", callback_data="monetization_back")
    )

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def get_referral_keyboard(referral_link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📨 Пригласить друга", switch_inline_query=referral_link)],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monetization_back")]
    ])


def get_main_monetization_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance"),
            InlineKeyboardButton(text="👥 Реферальная ссылка", callback_data="monetization_referral")
        ],
        [
            InlineKeyboardButton(text="📤 Загрузить видео", callback_data="upload_video"),
            InlineKeyboardButton(text="📚 Правила", callback_data="monetization_rules")
        ]
    ]

    if is_admin:
        keyboard.append([InlineKeyboardButton(text="✅ Одобрение", callback_data="review_pending_videos")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
