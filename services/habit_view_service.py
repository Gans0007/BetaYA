from aiogram import Bot, types
from datetime import datetime
import pytz
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.profile_settings_service import profile_settings_service

from database import get_pool


# =====================================================
# 🔹 Кнопки для карточки привычки
# =====================================================
async def get_habit_buttons(habit_id: int, user_id: int) -> InlineKeyboardMarkup:

    pool = await get_pool()
    async with pool.acquire() as conn:

        # Таймзона
        user_row = await conn.fetchrow(
            "SELECT timezone FROM users WHERE user_id=$1", user_id
        )
        user_tz = user_row["timezone"] if user_row and user_row["timezone"] else "Europe/Kyiv"
        tz = pytz.timezone(user_tz)
        today = datetime.now(tz).date()

        # Инфо о привычке
        habit = await conn.fetchrow("""
            SELECT done_days, days, is_challenge
            FROM habits WHERE id=$1
        """, habit_id)

        if not habit:
            return InlineKeyboardMarkup(inline_keyboard=[])

        done = habit["done_days"]
        total = habit["days"]
        is_challenge = habit["is_challenge"]

        keyboard_rows = []

        # ------------------------------------------------
        # 🔥 Челлендж
        # ------------------------------------------------
        if is_challenge:

            # Если челлендж выполнен — кнопок нет
            if done >= total:
                pass
            else:
                last = await conn.fetchrow("""
                    SELECT datetime FROM confirmations
                    WHERE user_id=$1 AND habit_id=$2
                    ORDER BY datetime DESC LIMIT 1
                """, user_id, habit_id)

                btn = "✅ Подтвердить"
                if last:
                    last_dt = last["datetime"].astimezone(tz)
                    if last_dt.date() == today:
                        btn = "♻️ Переподтвердить"

                keyboard_rows.append([
                    InlineKeyboardButton(text=btn, callback_data=f"confirm_{habit_id}"),
                    InlineKeyboardButton(text="🗑 Удалить", callback_data=f"ask_delete_{habit_id}")
                ])

        else:
            # ------------------------------------------------
            # 🔹 Привычка выполнена — Продлить/Завершить
            # ------------------------------------------------
            if done >= total:
                keyboard_rows.append([
                    InlineKeyboardButton(text="🔁 Продлить", callback_data=f"extend_{habit_id}"),
                    InlineKeyboardButton(text="✅ Завершить", callback_data=f"finish_{habit_id}")
                ])
            else:
                # ------------------------------------------------
                # 🔹 Обычная привычка
                # ------------------------------------------------
                last = await conn.fetchrow("""
                    SELECT datetime FROM confirmations
                    WHERE user_id=$1 AND habit_id=$2
                    ORDER BY datetime DESC LIMIT 1
                """, user_id, habit_id)

                btn = "✅ Подтвердить"
                if last:
                    last_dt = last["datetime"].astimezone(tz)
                    if last_dt.date() == today:
                        btn = "♻️ Переподтвердить"

                keyboard_rows.append([
                    InlineKeyboardButton(text=btn, callback_data=f"confirm_{habit_id}"),
                    InlineKeyboardButton(text="🗑 Удалить", callback_data=f"ask_delete_{habit_id}")
                ])

        # ------------------------------------------------
        # 🔹 Кнопка "Вернуться к списку"
        # ------------------------------------------------
        keyboard_rows.append([
            InlineKeyboardButton(
                text="⬅️ Вернуться к списку",
                callback_data="back_from_card"
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

# =====================================================
# 🔹 Карточка привычки/челленджа
# =====================================================
async def send_habit_card(source, habit, user_id: int):
    """
    source — может быть message или chat
    поэтому мы безопасно достаём bot и chat_id
    """

    # Достаём bot
    if isinstance(source, types.Message):
        bot: Bot = source.bot
        chat_id = source.chat.id
    else:
        # Это объект Chat
        bot: Bot = source.bot
        chat_id = source.id

    done = habit["done_days"]
    total = habit["days"]
    progress = int((done / total) * 100) if total > 0 else 0

    diff_text = {
        1: "⭐ Легко",
        2: "⭐⭐ Средне",
        3: "⭐⭐⭐ Сложно",
    }.get(habit["difficulty"], "⭐ Легко")

    if habit["last_date"]:
        tz = pytz.timezone(habit["timezone"] or "Europe/Kyiv")
        last_text = habit["last_date"].astimezone(tz).strftime("%d.%m.%Y %H:%M")
    else:
        last_text = "ещё не подтверждалась"

    header = "🔥 Активный челлендж:" if habit["is_challenge"] else "⚡️ Активная привычка:"

    text = (
        f"{header}\n\n"
        f"🏁 *Название:* {habit['name']}\n"
        f"📖 *Описание:* {habit['description']}\n"
        f"📅 *Прогресс:* {done} из {total} ({progress}%)\n"
        f"🎯 *Сложность:* {diff_text}\n"
        f"🕒 *Последнее подтверждение:* {last_text}"
    )

    keyboard = await get_habit_buttons(habit["id"], user_id)

    # 🔥 Правильный способ в Aiogram 3.0
    await bot.send_message(
        chat_id,
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )



# =====================================================
# 🔹 Список активных привычек
# =====================================================
async def build_active_list(user_id: int):

    # 🔹 Настройки пользователя
    settings = await profile_settings_service.get_settings_for_user(user_id)
    share_on = settings["share_on"]

    pool = await get_pool()
    async with pool.acquire() as conn:

        # 🔹 Таймзона пользователя
        user_row = await conn.fetchrow(
            "SELECT timezone FROM users WHERE user_id=$1", user_id
        )
        user_tz = user_row["timezone"] if user_row and user_row["timezone"] else "Europe/Kyiv"
        tz = pytz.timezone(user_tz)
        today = datetime.now(tz).date()

        rows = await conn.fetch("""
            SELECT id, name, is_challenge
            FROM habits
            WHERE user_id=$1 AND is_active=TRUE
            ORDER BY created_at ASC
        """, user_id)

        if not rows:
            return None, None, []

        buttons = []

        for row in rows:
            habit_id = row["id"]
            title = row["name"]

            # 🔹 Проверяем подтверждение за сегодня
            last = await conn.fetchrow("""
                SELECT datetime
                FROM confirmations
                WHERE user_id=$1 AND habit_id=$2
                ORDER BY datetime DESC
                LIMIT 1
            """, user_id, habit_id)

            confirmed_today = False
            if last:
                last_dt = last["datetime"].astimezone(tz)
                confirmed_today = last_dt.date() == today

            # 🔹 Формируем текст кнопки
            if row["is_challenge"]:
                title = f"🔥 {title}"

            if confirmed_today:
                title = f"{title} 😎"

            buttons.append([
                InlineKeyboardButton(
                    text=title,
                    callback_data=f"habit_{habit_id}"
                )
            ])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    text = (
        "📋 *Твои активные привычки:*\n\n"
        f"📢 Публикация медиа: "
        f"{'🟢 Вкл' if share_on else '⚪ Выкл'}\n\n"
        "Нажми на любую, чтобы открыть карточку 👇"
    )

    return text, kb, rows

