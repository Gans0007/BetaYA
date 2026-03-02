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

    current_level, next_level, need = await affiliate_service.get_affiliate_level_info(
        user_id
    )

    bot_username = (await callback.message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={dashboard['code']}"

    active = dashboard["active"]
    invited = dashboard["invited"]
    earned = round(dashboard["payments"], 2)
    paid_out = round(dashboard["paid_out"], 2)

    available = round(earned - paid_out, 2)

    if next_level:
        bar = build_progress_bar(active, next_level["min_active"])
        progress_block = (
            "--------------------------------------\n"
            f"🚀 До {next_level['title']} ({next_level['min_active']} активных)\n"
            f"{bar:<20} {active} / {next_level['min_active']}\n"
            f"Ещё активных:        {need}\n"
            f"Будет доход:         {next_level['percent']}%\n"
        )
    else:
        progress_block = (
            "--------------------------------------\n"
            "🔥 Максимальный уровень достигнут\n"
        )

    text = (
        "📊 <b>Партнёрский кабинет</b>\n\n"
        "<pre>"
        f"🏆 Уровень:             {current_level['emoji']} {current_level['title']}\n"
        f"📈 Доход:               {current_level['percent']}%\n"
        "--------------------------------------\n"
        f"💰 Заработано:          {earned} USDT\n"
        f"💸 Выплачено:           {paid_out} USDT\n"
        f"💳 Доступно:            {available} USDT\n"
        "--------------------------------------\n"
        f"👥 Всего в команде:     {invited}\n"
        f"🟢 Активных:            {active}\n"
        f"{progress_block}"
        "--------------------------------------\n"
        f"🔗 Твоя ссылка:\n"
        f"{ref_link}\n"
        "</pre>"
    )


    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 Поделиться ссылкой",
                    switch_inline_query=ref_link
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Рефералы",
                    callback_data="affiliate_referrals_list"
                ),
                InlineKeyboardButton(
                    text="💰 Выплаты",
                    callback_data="affiliate_payments_list"
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
        text,
        parse_mode="HTML",
        reply_markup=kb,
        disable_web_page_preview=True
    )
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

def build_progress_bar(current: int, total: int, length: int = 10):
    if not total or total <= 0:
        return "□" * length

    ratio = min(current / total, 1)
    filled = int(ratio * length)
    return "■" * filled + "□" * (length - filled)
