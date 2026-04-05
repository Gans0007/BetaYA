from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from core.database import get_pool
from handlers.day_plan_fsm import AddTaskFSM

router = Router()


# ================================
# 📋 РЕНДЕР ЗАДАЧ
# ================================
async def render_tasks(message, user_id: int, date, is_evening: bool, edit: bool = False):
    pool = await get_pool()

    async with pool.acquire() as conn:
        tasks = await conn.fetch(
            """
            SELECT id, text, status 
            FROM daily_tasks
            WHERE user_id=$1 
            AND planned_for_date=$2
            AND is_deleted=FALSE
            ORDER BY position, id
            """,
            user_id,
            date
        )

    text = "📋 <b>Твои задачи:</b>\n\n"
    keyboard = []

    if not tasks:
        if is_evening:
            text += (
                "У тебя пока нет задач на завтра\n\n"
                "Самое время спланировать день 🔥"
            )
        else:
            text += (
                "Ты ещё не запланировал день ⚡\n\n"
                "Планирование доступно вечером\n"
                "🕗 с 20:00 до 23:00\n\n"
                "Возвращайся позже и распланируй завтрашний день 💪"
            ) 
    else:
        for i, task in enumerate(tasks, start=1):
            status_icon = {
                "pending": "⏳",
                "done": "✅",
                "failed": "❌"
            }.get(task["status"], "⏳")

            # 🔥 ЗАЧЕРКИВАНИЕ
            task_text = task["text"]
            if task["status"] == "done":
                task_text = f"<s>{task_text}</s>"

            text += (
                f"<b>{i}. {task_text}</b>\n"
                f"Статус: {status_icon}\n\n"
            )

        # 🔥 ОДНА СТРОКА КНОПОК
        if not is_evening:
            row = []

            for i in range(1, len(tasks) + 1):
                row.append(
                    InlineKeyboardButton(
                        text=f"{i}✅",
                        callback_data=f"task_done_index_{i}"
                    )
                )

            keyboard.append(row)

        # 🌙 ВЕЧЕР (удаление)
        if is_evening:
            for task in tasks:
                keyboard.append([
                    InlineKeyboardButton(
                        text="🗑 Удалить",
                        callback_data=f"task_delete_{task['id']}"
                    )
                ])

    # ➕ ДОБАВИТЬ
    if is_evening:
        keyboard.append([
            InlineKeyboardButton(
                text="➕ Добавить задачу",
                callback_data="task_add"
            )
        ])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if edit:
        await message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=markup)


# ================================
# 📋 ОТКРЫТИЕ ПЛАНА
# ================================
@router.message(lambda m: m.text and "План на завтра" in m.text)
async def show_day_plan(message: types.Message):
    user_id = message.from_user.id

    pool = await get_pool()
    async with pool.acquire() as conn:
        tz_name = await conn.fetchval(
            "SELECT timezone FROM users WHERE user_id=$1",
            user_id
        )

    tz_name = tz_name or "Europe/Kyiv"

    try:
        now = datetime.now(ZoneInfo(tz_name))
    except Exception:
        now = datetime.now(ZoneInfo("Europe/Kyiv"))

    hour = now.hour

    if 20 <= hour < 23:
        tomorrow = (now + timedelta(days=1)).date()
        await render_tasks(message, user_id, tomorrow, is_evening=True)
        return

    today = now.date()
    await render_tasks(message, user_id, today, is_evening=False)


# ================================
# ➕ ДОБАВЛЕНИЕ
# ================================
@router.callback_query(lambda c: c.data == "task_add")
async def add_task_inline(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AddTaskFSM.waiting_for_text)
    await callback.message.answer("✍️ Введи задачу:")


# ================================
# 💾 СОХРАНЕНИЕ
# ================================
@router.message(AddTaskFSM.waiting_for_text)
async def save_task(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip()

    if not text:
        await message.answer("❗ Пустая задача")
        return

    if len(text) < 2:
        await message.answer("❗ Слишком короткая задача")
        return

    if len(text) > 100:
        await message.answer("❗ Слишком длинная задача")
        return

    pool = await get_pool()

    async with pool.acquire() as conn:
        tz_name = await conn.fetchval(
            "SELECT timezone FROM users WHERE user_id=$1",
            user_id
        )

    tz_name = tz_name or "Europe/Kyiv"
    now = datetime.now(ZoneInfo(tz_name))
    tomorrow = (now + timedelta(days=1)).date()

    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO daily_tasks (user_id, text, planned_for_date)
                VALUES ($1, $2, $3)
                """,
                user_id,
                text,
                tomorrow
            )
    except Exception:
        await message.answer("❗ Такая задача уже есть")
        return

    await state.clear()
    await message.answer("✅ Задача добавлена")

    await render_tasks(message, user_id, tomorrow, is_evening=True)


# ================================
# 🔥 DONE ПО ИНДЕКСУ
# ================================
@router.callback_query(lambda c: c.data.startswith("task_done_index_"))
async def task_toggle_by_index(callback: types.CallbackQuery):
    index = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id

    pool = await get_pool()

    now = datetime.now(ZoneInfo("Europe/Kyiv"))
    today = now.date()

    async with pool.acquire() as conn:
        tasks = await conn.fetch(
            """
            SELECT id, status
            FROM daily_tasks
            WHERE user_id=$1 
            AND planned_for_date=$2
            AND is_deleted=FALSE
            ORDER BY position, id
            """,
            user_id,
            today
        )

        if index <= len(tasks):
            task = tasks[index - 1]
            task_id = task["id"]
            current_status = task["status"]

            # 🔥 TOGGLE
            new_status = "pending" if current_status == "done" else "done"

            await conn.execute(
                "UPDATE daily_tasks SET status=$1 WHERE id=$2",
                new_status,
                task_id
            )

    await callback.answer("🔁 Обновлено")

    await render_tasks(
        callback.message,
        user_id,
        today,
        is_evening=False,
        edit=True
    )


# ================================
# 🗑 DELETE
# ================================
@router.callback_query(lambda c: c.data.startswith("task_delete_"))
async def task_delete(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[-1])

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE daily_tasks SET is_deleted=TRUE WHERE id=$1",
            task_id
        )

    await callback.answer("🗑 Удалено")

    user_id = callback.from_user.id
    now = datetime.now(ZoneInfo("Europe/Kyiv"))
    tomorrow = (now + timedelta(days=1)).date()

    await render_tasks(
        callback.message,
        user_id,
        tomorrow,
        is_evening=True,
        edit=True
    )


# ================================
# DEBUG
# ================================
@router.message()
async def debug_day_plan_all(message: types.Message):
    print("DAY_PLAN DEBUG:", repr(message.text))