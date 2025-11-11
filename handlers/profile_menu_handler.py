from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

router = Router()


# -------------------------------
# 👤 Главное меню "Профиль"
# -------------------------------
@router.message(lambda m: m.text == "👤 Профиль")
async def show_profile_menu(message: types.Message):
    """Показывает кнопки 'Настройки' и 'Статистика'"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="profile_settings"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="profile_stats"),
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
    """Возвращает в меню профиля"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="profile_settings"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="profile_stats"),
            ]
        ]
    )

    await callback.message.edit_text(
        "👤 *Профиль*\n\nВыбери нужный раздел:",
        parse_mode="Markdown",
        reply_markup=kb
    )
    await callback.answer()
