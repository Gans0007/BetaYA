from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from core.database import get_pool
from handlers.day_plan_fsm import AddTaskFSM

router = Router()


# ================================
# 📋 РЕНДЕР ЗАДАЧ (NEW UI)
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

    text = "📋 <b>План</b>\n\n"
    keyboard = []

    if not tasks:
        text += "Нет задач\n\nДобавь первую 🔥"

    else:
        for i, task in enumerate(tasks, start=1):
            status = task["status"]

            status_icon = {
                "pending": "⏳",
                "done": "✅",
                "failed": "❌"
            }.get(status, "⏳")

            task_text = task["text"]

            # 🔥 зачёркивание выполненной
            if status == "done":
                task_text = f"<s>{task_text}</s>"

            # 🧠 компактный UI
            text += f"{i}. {task_text} {status_icon}\n\n"

            # 🎯 кнопки
            if is_evening:
                keyboard.append([
                    InlineKeyboardButton(
                        text="🗑",
                        callback_data=f"task_delete_{task['id']}"
                    )
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(
                        text="✅",
                        callback_data=f"task_done_{task['id']}"
                    ),
                    InlineKeyboardButton(
                        text="❌",
                        callback_data=f"task_fail_{task['id']}"
                    )
                ])

    # ➕ добавить
    if is_evening:
        keyboard.append([
            InlineKeyboardButton(
                text="➕ Добавить",
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

    await message.answer("✅ Добавлено")

    await render_tasks(message, user_id, tomorrow, is_evening=True)


# ================================
# ✅ DONE
# ================================
@router.callback_query(lambda c: c.data.startswith("task_done_"))
async def task_done(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[-1])

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE daily_tasks SET status='done' WHERE id=$1",
            task_id
        )

    await callback.answer("✅")

    user_id = callback.from_user.id
    now = datetime.now(ZoneInfo("Europe/Kyiv"))

    await render_tasks(
        callback.message,
        user_id,
        now.date(),
        is_evening=False,
        edit=True
    )


# ================================
# ❌ FAILED
# ================================
@router.callback_query(lambda c: c.data.startswith("task_fail_"))
async def task_fail(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[-1])

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE daily_tasks SET status='failed' WHERE id=$1",
            task_id
        )

    await callback.answer("❌")

    user_id = callback.from_user.id
    now = datetime.now(ZoneInfo("Europe/Kyiv"))

    await render_tasks(
        callback.message,
        user_id,
        now.date(),
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

    await callback.answer("🗑")

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
# 🧪 DEBUG
# ================================
@router.message()
async def debug_day_plan_all(message: types.Message):
    print("DAY_PLAN DEBUG:", repr(message.text))