from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

from services.affiliate_service import affiliate_service

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

# -------------------------------------------------
# 🧩 Утилита — красиво показывать имя пользователя
# -------------------------------------------------
def format_user(row):
    username = row.get("username")
    nickname = row.get("nickname")
    user_id = row.get("user_id")

    if username:
        return f"@{username}"
    if nickname:
        return f"{nickname}"
    return f"ID:{user_id}"


# -------------------------------------------------
# 💼 Меню партнёрки
# -------------------------------------------------
@router.callback_query(lambda c: c.data == "affiliate_menu")
async def show_affiliate_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logging.info(f"[AFFILIATE] Пользователь {user_id} открыл меню партнёрки")

    dashboard = await affiliate_service.get_affiliate_dashboard(user_id)
    code = dashboard["code"]

    bot_username = (await callback.message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={code}"

    text = (
        "💼 Партнёрская программа\n\n"
        f"🔗 Твой реферальный код: {code}\n"
        f"🌐 Реферальная ссылка:\n{ref_link}\n\n"
        f"👥 Всего приглашено: {dashboard['invited']}\n"
        f"🔥 Активных: {dashboard['active']}\n\n"
        f"💰 Заработано: {dashboard['payments']}$\n"
        f"🏦 Выплачено: {dashboard['paid_out']}$\n\n"
        "Ты получаешь 20% от стоимости подписки за каждого активного реферала."
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Мои рефералы", callback_data="affiliate_referrals_list")],
            [InlineKeyboardButton(text="💰 Выплаты", callback_data="affiliate_payments_list")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile_menu")]
        ]
    )

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


# -------------------------------------------------
# 👥 Список рефералов
# -------------------------------------------------
@router.callback_query(lambda c: c.data.startswith("affiliate_referrals"))
async def show_affiliate_referrals(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    raw_data = callback.data

    logging.info(
        f"👥 [ПАРТНЁРКА] Пользователь {user_id} открыл список рефералов "
        f"(callback_data='{raw_data}')"
    )

    # -------------------------------
    # 📄 Определяем страницу
    # -------------------------------
    parts = raw_data.split(":")
    try:
        page = int(parts[1]) if len(parts) > 1 else 1
    except ValueError:
        logging.warning(
            f"⚠️ [ПАРТНЁРКА] Некорректный номер страницы у пользователя {user_id}: "
            f"{parts}"
        )
        page = 1

    PER_PAGE = 10

    logging.info(
        f"📄 [ПАРТНЁРКА] Загружаем страницу {page} "
        f"(по {PER_PAGE} рефералов на страницу) для пользователя {user_id}"
    )

    # -------------------------------
    # 📦 Получаем данные
    # -------------------------------
    data = await affiliate_service.get_my_referrals_paginated(
        user_id=user_id,
        page=page,
        per_page=PER_PAGE
    )

    total = data["total"]
    referrals = data["items"]

    logging.info(
        f"📊 [ПАРТНЁРКА] Найдено рефералов всего: {total}. "
        f"Показано на странице {page}: {len(referrals)}"
    )

    # -------------------------------
    # 📝 Формируем текст
    # -------------------------------
    if total == 0:
        text = "😔 У тебя пока нет рефералов."
        logging.info(
            f"ℹ️ [ПАРТНЁРКА] У пользователя {user_id} нет рефералов"
        )
    else:
        pages = (total + PER_PAGE - 1) // PER_PAGE
        text = f"👥 Твои рефералы (стр. {page}/{pages}):\n\n"

        for r in referrals:
            name = format_user(r)
            status = "🟢 активен" if r["is_active"] else "🔴 не активен"
            text += f"{name} — {status}\n"

    # -------------------------------
    # 🔘 Кнопки навигации
    # -------------------------------
    nav_buttons = []

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"affiliate_referrals:{page - 1}"
            )
        )

    if page * PER_PAGE < total:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"affiliate_referrals:{page + 1}"
            )
        )

    keyboard = []
    if nav_buttons:
        keyboard.append(nav_buttons)

        logging.info(
            f"🔁 [ПАРТНЁРКА] Навигация: "
            f"{'назад ' if page > 1 else ''}"
            f"{'вперёд' if page * PER_PAGE < total else ''}"
        )

    keyboard.append(
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="affiliate_menu")]
    )

    # -------------------------------
    # ✉️ Отправляем сообщение
    # -------------------------------
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    logging.info(
        f"✅ [ПАРТНЁРКА] Страница {page} успешно показана пользователю {user_id}"
    )

    await callback.answer()


# -------------------------------------------------
# 💰 История выплат
# -------------------------------------------------
@router.callback_query(lambda c: c.data == "affiliate_payments_list")
async def show_affiliate_payments(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logging.info(f"[AFFILIATE] Пользователь {user_id} смотрит выплаты")

    payments = await affiliate_service.get_affiliate_payments_list(user_id)

    if not payments:
        text = "💸 Пока ещё не было активных рефералов."
    else:
        text = "💰 Выплаты:\n\n"
        for p in payments:
            name = format_user(p)
            amount = p.get("amount", "?")
            created_at = p.get("created_at")

            date_text = created_at.strftime("%d.%m.%Y") if created_at else ""

            text += f"• {name} → +{amount}$ ({date_text})\n"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="affiliate_menu")]
        ]
    )

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()
