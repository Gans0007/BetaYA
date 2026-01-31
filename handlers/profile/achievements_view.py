from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


# -------------------------------
# 🏆 Достижения — категории
# -------------------------------
@router.callback_query(lambda c: c.data == "profile:achievements")
async def show_achievement_categories(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logging.info(f"[ACHIEVEMENTS] Пользователь {user_id} открыл категории достижений")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔥 Дисциплина",
                    callback_data="achievements:category:discipline"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🥊 Тело",
                    callback_data="achievements:category:body"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧠 Ум",
                    callback_data="achievements:category:mind"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👑 Статус",
                    callback_data="achievements:category:status"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Деньги",
                    callback_data="achievements:category:money"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_to_profile_menu"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "🏆 *Достижения*\n\nВыбери категорию:",
        parse_mode="Markdown",
        reply_markup=kb
    )

    await callback.answer()

# -------------------------------
# 🚧 Заглушка категорий достижений
# -------------------------------
@router.callback_query(lambda c: c.data.startswith("achievements:category:"))
async def achievements_category_stub(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    category = callback.data.split(":")[-1]

    logging.info(
        f"[ACHIEVEMENTS] Пользователь {user_id} открыл категорию {category} (в разработке)"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="profile:achievements"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "🚧 *Раздел в разработке*\n\n"
        "Мы уже работаем над системой достижений.\n"
        "Совсем скоро этот раздел станет доступен 👀",
        parse_mode="Markdown",
        reply_markup=kb
    )

    await callback.answer()

