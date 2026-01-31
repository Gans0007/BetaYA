#handlers/profile/menu
from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


# -------------------------------
# 👤 Главное меню "Профиль"
# -------------------------------
@router.message(lambda m: m.text == "👤 Профиль")
async def show_profile_menu(message: types.Message):
    user_id = message.from_user.id
    logging.info(f"[MENU PROFILE] Пользователь {user_id} открыл меню профиля")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="profile_settings"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="profile_stats"),
                InlineKeyboardButton(text="💼 Партнёрка", callback_data="affiliate_menu"),
            ],
            [
                InlineKeyboardButton(text="🏆 Достижения", callback_data="profile:achievements"),
            ]
        ]
    )


    await message.answer(
        "👤 *Профиль*\n\nВыбери нужный раздел:",
        parse_mode="Markdown",
        reply_markup=kb
    )


# -------------------------------
# ⬅️ Возврат в меню профиля
# -------------------------------
@router.callback_query(lambda c: c.data == "back_to_profile_menu")
async def back_to_profile_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logging.info(f"[MENU PROFILE] Пользователь {user_id} вернулся в меню профиля")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="profile_settings"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="profile_stats"),
                InlineKeyboardButton(text="💼 Партнёрка", callback_data="affiliate_menu"),
            ],
            [
                InlineKeyboardButton(text="🏆 Достижения", callback_data="profile:achievements"),
            ] 
        ]
)


    await callback.message.edit_text(
        "👤 *Профиль*\n\nВыбери нужный раздел:",
        parse_mode="Markdown",
        reply_markup=kb
    )

    await callback.answer()
