from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from services.profile_menu_service import profile_service

router = Router()


# -------------------------------
# 👤 Главное меню "Профиль"
# -------------------------------
@router.message(lambda m: m.text == "👤 Профиль")
async def show_profile_menu(message: types.Message):
    user_id = message.from_user.id

    # получаем статус партнёра через сервис
    is_affiliate = await profile_service.user_is_affiliate(user_id)

    row = [
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="profile_settings"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="profile_stats"),
    ]

    if is_affiliate:
        row.append(InlineKeyboardButton(text="💼 Партнёрка", callback_data="affiliate_menu"))

    kb = InlineKeyboardMarkup(inline_keyboard=[row])

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

    # опять — только через сервис
    is_affiliate = await profile_service.user_is_affiliate(user_id)

    row = [
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="profile_settings"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="profile_stats"),
    ]

    if is_affiliate:
        row.append(InlineKeyboardButton(text="💼 Партнёрка", callback_data="affiliate_menu"))

    kb = InlineKeyboardMarkup(inline_keyboard=[row])

    await callback.message.edit_text(
        "👤 *Профиль*\n\nВыбери нужный раздел:",
        parse_mode="Markdown",
        reply_markup=kb
    )
    await callback.answer()
