from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_pool
from datetime import datetime
import pytz

router = Router()

# -------------------------------
# 🔹 FSM состояния
# -------------------------------
class ConfirmHabitFSM(StatesGroup):
    waiting_for_media = State()


# -------------------------------
# 🔹 Кнопка отмены
# -------------------------------
def cancel_kb(habit_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_media_{habit_id}")]]
    )


# -------------------------------
# 🔹 Кнопки "Подтвердить" / "Удалить" (динамические)
# -------------------------------
async def get_habit_buttons(habit_id: int, user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        user_row = await conn.fetchrow("SELECT timezone FROM users WHERE user_id = $1", user_id)
        user_tz = user_row["timezone"] if user_row and user_row["timezone"] else "Europe/Kyiv"
        user_timezone = pytz.timezone(user_tz)
        user_now = datetime.now(user_timezone)

        habit = await conn.fetchrow("""
            SELECT done_days, days, is_challenge
            FROM habits
            WHERE id = $1
        """, habit_id)

        if not habit:
            return InlineKeyboardMarkup(inline_keyboard=[])

        done_days = habit["done_days"]
        total_days = habit["days"]
        is_challenge = habit["is_challenge"]

        # 🏆 Если это челлендж
        if is_challenge:
            # если челлендж завершён — кнопок нет (автозавершение)
            if done_days >= total_days:
                return InlineKeyboardMarkup(inline_keyboard=[])
            else:
                # Проверяем последнее подтверждение (чтобы заменить текст кнопки)
                row = await conn.fetchrow("""
                    SELECT datetime FROM confirmations
                    WHERE user_id = $1 AND habit_id = $2
                    ORDER BY datetime DESC LIMIT 1
                """, user_id, habit_id)

                button_text = "✅ Подтвердить"
                if row:
                    last_time = row["datetime"].astimezone(user_timezone)
                    if last_time.date() == user_now.date():
                        button_text = "♻️ Переподтвердить"

                # активный челлендж → кнопки Подтвердить / Переподтвердить и Удалить
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text=button_text, callback_data=f"confirm_{habit_id}"),
                            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"ask_delete_{habit_id}")
                        ]
                    ]
                )
                return keyboard

        # 💪 Если это привычка и она завершена — показать “Продлить / Завершить”
        if done_days >= total_days:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="🔁 Продлить", callback_data=f"extend_{habit_id}"),
                        InlineKeyboardButton(text="✅ Завершить", callback_data=f"finish_{habit_id}")
                    ]
                ]
            )

        else:
            # ⚙️ Обычный случай — активная привычка
            row = await conn.fetchrow("""
                SELECT datetime FROM confirmations
                WHERE user_id = $1 AND habit_id = $2
                ORDER BY datetime DESC LIMIT 1
            """, user_id, habit_id)

            button_text = "✅ Подтвердить"
            if row:
                last_time = row["datetime"].astimezone(user_timezone)
                if last_time.date() == user_now.date():
                    button_text = "♻️ Переподтвердить"

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=button_text, callback_data=f"confirm_{habit_id}"),
                        InlineKeyboardButton(text="🗑 Удалить", callback_data=f"ask_delete_{habit_id}")
                    ]
                ]
            )

    return keyboard


# -------------------------------
# 🔹 Обработка "Подтвердить"
# -------------------------------
@router.callback_query(F.data.startswith("confirm_"))
async def confirm_habit_start(callback: types.CallbackQuery, state: FSMContext):
    habit_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    pool = await get_pool()
    async with pool.acquire() as conn:
        user_row = await conn.fetchrow("SELECT timezone FROM users WHERE user_id = $1", user_id)
        user_tz = user_row["timezone"] if user_row and user_row["timezone"] else "Europe/Kyiv"
        user_timezone = pytz.timezone(user_tz)
        user_now = datetime.now(user_timezone)

        row = await conn.fetchrow("""
            SELECT id, datetime FROM confirmations
            WHERE user_id = $1 AND habit_id = $2
            ORDER BY datetime DESC LIMIT 1
        """, user_id, habit_id)

        if row:
            last_time = row["datetime"].astimezone(user_timezone)
            if last_time.date() == user_now.date():
                await state.update_data(habit_id=habit_id, reverify=True)
                await state.set_state(ConfirmHabitFSM.waiting_for_media)
                await callback.message.answer(
                    "♻️ Ты уже подтверждал сегодня.\n"
                    "Пришли новое фото/видео, чтобы *переподтвердить* привычку.",
                    parse_mode="Markdown",
                    reply_markup=cancel_kb(habit_id)
                )
                await callback.answer()
                return

        await state.update_data(habit_id=habit_id, reverify=False)
        await state.set_state(ConfirmHabitFSM.waiting_for_media)
        await callback.message.answer(
            "📸 Пришли фото, видео или кружочек, подтверждающий выполнение привычки 💪",
            reply_markup=cancel_kb(habit_id)
        )

    await callback.answer()


# -------------------------------
# 🔹 Отмена во время ожидания медиа
# -------------------------------
@router.callback_query(F.data.startswith("cancel_media_"))
async def cancel_media(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❎ Подтверждение отменено.")
    await callback.answer()


# -------------------------------
# 🔹 Получаем медиафайл
# -------------------------------
@router.message(ConfirmHabitFSM.waiting_for_media)
async def receive_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    habit_id = data.get("habit_id")
    reverify = data.get("reverify", False)
    user_id = message.from_user.id

    pool = await get_pool()
    file_id = None
    file_type = None

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.video_note:
        file_id = message.video_note.file_id
        file_type = "circle"
    else:
        await message.answer("⚠️ Нужно отправить фото, видео или кружочек 🎥")
        return

    async with pool.acquire() as conn:
        # 🧩 Проверяем, существует ли привычка / челлендж (может быть уже завершён)
        habit_exists = await conn.fetchval("SELECT COUNT(*) FROM habits WHERE id = $1", habit_id)
        if habit_exists == 0:
            await message.answer("⚠️ Эта привычка или челлендж уже завершён и больше не активен.")
            await state.clear()
            return

        if reverify:
            await conn.execute("""
                UPDATE confirmations
                SET file_id = $1, file_type = $2, datetime = NOW()
                WHERE user_id = $3 AND habit_id = $4
            """, file_id, file_type, user_id, habit_id)

            await message.answer("♻️ Видео обновлено. Переподтверждение сохранено 💪")

        else:
            # Добавляем новое подтверждение
            await conn.execute("""
                INSERT INTO confirmations (user_id, habit_id, datetime, file_id, file_type, confirmed)
                VALUES ($1, $2, NOW(), $3, $4, TRUE)
            """, user_id, habit_id, file_id, file_type)

            # Увеличиваем количество выполненных дней
            await conn.execute("""
                UPDATE habits
                SET done_days = done_days + 1
                WHERE id = $1
            """, habit_id)

            # 🔥 Проверка автозавершения челленджа
            habit = await conn.fetchrow("""
                SELECT user_id, name, description, days, done_days, is_challenge, challenge_id
                FROM habits
                WHERE id = $1
            """, habit_id)

            if habit["is_challenge"] and habit["done_days"] >= habit["days"]:
                # Проверяем, был ли челлендж уже завершён раньше
                existing = await conn.fetchrow("""
                    SELECT repeat_count FROM completed_challenges
                    WHERE user_id = $1 AND challenge_id = $2
                """, habit["user_id"], habit["challenge_id"])

                if existing:
                    new_count = min(existing["repeat_count"] + 1, 3)
                    await conn.execute("""
                        UPDATE completed_challenges
                        SET repeat_count = $1, completed_at = NOW()
                        WHERE user_id = $2 AND challenge_id = $3
                    """, new_count, habit["user_id"], habit["challenge_id"])
                    stars = new_count
                else:
                    await conn.execute("""
                        INSERT INTO completed_challenges (user_id, challenge_name, level_key, challenge_id, repeat_count)
                        VALUES ($1, $2, 'auto', $3, 1)
                    """, habit["user_id"], habit["name"], habit["challenge_id"])
                    stars = 1

                # 🔹 Увеличиваем общий счётчик завершённых челленджей
                await conn.execute("""
                    UPDATE users
                    SET finished_challenges = finished_challenges + 1
                    WHERE user_id = $1
                """, habit["user_id"])

                # 🌟 Добавляем звёзды пользователю (по реальной разнице)
                if existing:
                    stars_gained = new_count - existing["repeat_count"]
                else:
                    stars_gained = 1  # если челлендж впервые завершён

                await conn.execute("""
                    UPDATE users
                    SET total_stars = total_stars + $1
                    WHERE user_id = $2
                """, stars_gained, habit["user_id"])

                # Удаляем челлендж из активных привычек
                await conn.execute("DELETE FROM habits WHERE id = $1", habit_id)

                # Получаем обновлённое количество завершённых челленджей и звёзд
                user_stats = await conn.fetchrow("""
                    SELECT finished_challenges, total_stars
                    FROM users
                    WHERE user_id = $1
                """, habit["user_id"])
                total_finished = user_stats["finished_challenges"]
                total_stars = user_stats["total_stars"]

                stars_display = "⭐" * stars + "☆" * (3 - stars)
                await message.answer(
                    f"🔥 Ты красавчик!\n\n"
                    f"Челлендж *{habit['name']}* выполнен и закрыт на {stars_display}\n\n"
                    f"🏆 Он добавлен в твою статистику!\n"
                    f"Продолжай в том же духе 💪",
                    parse_mode="Markdown"
                )
            else:
                await message.answer("✅ Привычка подтверждена! Отличная работа 💪")

    await state.clear()

# -------------------------------
# 🔹 Шаг 1: Запрос подтверждения удаления
# -------------------------------
@router.callback_query(F.data.startswith("ask_delete_"))
async def ask_delete_confirmation(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"delete_habit_{habit_id}"),
                InlineKeyboardButton(text="❌ Нет", callback_data="cancel_delete")
            ]
        ]
    )

    await callback.message.edit_text(
        "⚠️ Если ты удалишь привычку, весь прогресс будет потерян.\n\n"
        "Ты уверен, что хочешь удалить её?",
        reply_markup=keyboard
    )
    await callback.answer()


# -------------------------------
# 🔹 Шаг 2: Подтверждение удаления
# -------------------------------
@router.callback_query(F.data.startswith("delete_habit_"))
async def delete_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM confirmations WHERE habit_id = $1", habit_id)
        await conn.execute("DELETE FROM habits WHERE id = $1", habit_id)

    await callback.message.edit_text("🗑 Привычка удалена вместе с прогрессом.")
    await callback.answer()


# -------------------------------
# 🔹 Шаг 3: Отмена удаления
# -------------------------------
@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: types.CallbackQuery):
    # Восстанавливаем карточку привычки
    # Получаем habit_id из текста предыдущего сообщения
    # (из callback'а перед этим — ask_delete_confirmation)
    message_text = callback.message.text

    # Пробуем извлечь ID привычки из предыдущего callback_data
    # (берем из inline-кнопок, если они остались)
    keyboard = callback.message.reply_markup
    habit_id = None

    if keyboard and keyboard.inline_keyboard:
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data and button.callback_data.startswith("delete_habit_"):
                    habit_id = int(button.callback_data.split("_")[2])
                    break

    if not habit_id:
        await callback.message.edit_text("❎ Ошибка восстановления карточки.")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        habit = await conn.fetchrow("""
            SELECT name, description, days, done_days
            FROM habits
            WHERE id = $1
        """, habit_id)

    if habit:
        name = habit["name"]
        desc = habit["description"]
        total_days = habit["days"]
        done = habit["done_days"]
        progress = int((done / total_days) * 100) if total_days > 0 else 0

        text = (
            f"🏁 {name}\n\n"
            f"📖 {desc}\n\n"
            f"📅 Прогресс: {done} из {total_days} дней ({progress}%)"
        )

        keyboard = await get_habit_buttons(habit_id, callback.from_user.id)
        await callback.message.edit_text(text, reply_markup=keyboard)
    else:
        await callback.message.edit_text("❎ Привычка не найдена.")

    await callback.answer()


# -------------------------------
# 🔹 Продление привычки
# -------------------------------
@router.callback_query(F.data.regexp(r"^extend_\d+$"))
async def extend_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[1])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"extend_yes_{habit_id}"),
                InlineKeyboardButton(text="❌ Нет", callback_data="extend_no")
            ]
        ]
    )

    await callback.message.edit_text(
        "🔁 Хочешь продлить привычку на 5 дней?",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.regexp(r"^extend_yes_\d+$"))
async def extend_habit_yes(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE habits
            SET days = days + 5
            WHERE id = $1
        """, habit_id)

        habit = await conn.fetchrow("""
            SELECT name, description, days, done_days
            FROM habits
            WHERE id = $1
        """, habit_id)

    text = (
        f"⚡️ Активная привычка:\n\n"
        f"📖 {habit['description']}\n"
        f"📅 Продлено: теперь {habit['days']} дней!\n"
        f"📊 Прогресс: {habit['done_days']} / {habit['days']}"
    )
    keyboard = await get_habit_buttons(habit_id, callback.from_user.id)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer("🔁 Привычка продлена на 5 дней!")


@router.callback_query(F.data == "extend_no")
async def extend_habit_no(callback: types.CallbackQuery):
    await callback.message.edit_text("❎ Продление отменено.")
    await callback.answer()


# -------------------------------
# 🔹 Завершение привычки (с подтверждением)
# -------------------------------
@router.callback_query(F.data.regexp(r"^finish_\d+$"))
async def finish_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[1])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"finish_yes_{habit_id}"),
                InlineKeyboardButton(text="❌ Нет", callback_data="finish_no")
            ]
        ]
    )

    await callback.message.edit_text(
        "🏁 Привычка будет завершена и добавлена в твою статистику.\n\n"
        "Ты уверен, что хочешь завершить?",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.regexp(r"^finish_yes_\d+$"))
async def finish_habit_yes(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Увеличиваем счётчик завершённых привычек
        await conn.execute("""
            UPDATE users
            SET finished_habits = finished_habits + 1
            WHERE user_id = $1
        """, user_id)

        # Удаляем привычку
        habit = await conn.fetchrow("""
            DELETE FROM habits
            WHERE id = $1
            RETURNING name
        """, habit_id)

        name = habit["name"] if habit else "Привычка"

        # Получаем обновлённое количество завершённых привычек
        user_stats = await conn.fetchrow("""
            SELECT finished_habits FROM users WHERE user_id = $1
        """, user_id)

    total_finished = user_stats["finished_habits"]

    await callback.message.edit_text(
        f"✅ {name} завершена и добавлена в твою статистику!\n\n"
        f"📊 Всего завершённых привычек: *{total_finished}*",
        parse_mode="Markdown"
    )
    await callback.answer("🎉 Привычка завершена!")


@router.callback_query(F.data == "finish_no")
async def finish_habit_no(callback: types.CallbackQuery):
    await callback.message.edit_text("❎ Завершение отменено.")
    await callback.answer()
