from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from core.database import get_pool
from handlers.day_plan_fsm import AddTaskFSM

router = Router()


# ================================
# 📋 РЕНДЕР
# ================================
async def render_tasks(message, user_id: int, is_evening: bool, edit: bool = False):
    pool = await get_pool()

    async with pool.acquire() as conn:
        tz_name = await conn.fetchval(
            "SELECT timezone FROM users WHERE user_id=$1",
            user_id
        )

    tz_name = tz_name or "Europe/Kyiv"
    now = datetime.now(ZoneInfo(tz_name))

    today = now.date()
    tomorrow = (now + timedelta(days=1)).date()

    # ===== сегодня =====
    async with pool.acquire() as conn:
        today_tasks = await conn.fetch(
            """
            SELECT id, text, status
            FROM daily_tasks
            WHERE user_id=$1 AND planned_for_date=$2 AND is_deleted=FALSE
            ORDER BY position, id
            """,
            user_id,
            today
        )

    # ===== завтра =====
    async with pool.acquire() as conn:
        tomorrow_tasks = await conn.fetch(
            """
            SELECT id, text, status
            FROM daily_tasks
            WHERE user_id=$1 AND planned_for_date=$2 AND is_deleted=FALSE
            ORDER BY position, id
            """,
            user_id,
            tomorrow
        )

    text = ""
    keyboard = []

    # ================================
    # 🌙 ВЕЧЕР
    # ================================
    if is_evening:

        # 📊 СЕГОДНЯ
        text += "📊 <b>Сегодня</b>\n\n"

        if not today_tasks:
            text += "Нет задач\n\n"
        else:
            for i, task in enumerate(today_tasks, 1):
                status_icon = "✅" if task["status"] == "done" else "❌"
                text += f"{i}. {task['text']} {status_icon}\n"

        text += "\n"

        # 📋 ЗАВТРА
        text += "📋 <b>План на завтра</b>\n\n"

        if not tomorrow_tasks:
            text += "Нет задач\n\nДобавь первую 🔥"
        else:
            for i, task in enumerate(tomorrow_tasks, 1):
                text += f"{i}. {task['text']}\n\n"

                keyboard.append([
                    InlineKeyboardButton(
                        text="🗑",
                        callback_data=f"task_delete_{task['id']}"
                    )
                ])

        keyboard.append([
            InlineKeyboardButton(
                text="➕ Добавить",
                callback_data="task_add"
            )
        ])

    # ================================
    # 🌅 ДЕНЬ
    # ================================
    else:
        text += "📋 <b>План на сегодня</b>\n\n"

        done_count = sum(1 for t in today_tasks if t["status"] == "done")
        total = len(today_tasks)

        if total > 0:
            text += f"🔥 {done_count}/{total} выполнено\n\n"

        if not today_tasks:
            text += "Нет задач"
        else:
            for i, task in enumerate(today_tasks, 1):
                status = task["status"]

                if status == "done":
                    task_text = f"<s>{task['text']}</s>"
                    icon = "✅"
                elif status == "failed":
                    task_text = task["text"]
                    icon = "❌"
                else:
                    task_text = task["text"]
                    icon = "⏳"

                text += f"{i}. {task_text} {icon}\n"

                keyboard.append([
                    InlineKeyboardButton(
                        text="✅",
                        callback_data=f"task_done_{task['id']}"
                    )
                ])

                text += "\n"

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if edit:
        await message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=markup)


# ================================
# 📋 ОТКРЫТИЕ
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
    now = datetime.now(ZoneInfo(tz_name))

    is_evening = 20 <= now.hour < 23

    await render_tasks(message, user_id, is_evening)


# ================================
# ➕ ДОБАВИТЬ
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

    pool = await get_pool()

    async with pool.acquire() as conn:
        tz_name = await conn.fetchval(
            "SELECT timezone FROM users WHERE user_id=$1",
            user_id
        )

    tz_name = tz_name or "Europe/Kyiv"
    now = datetime.now(ZoneInfo(tz_name))
    tomorrow = (now + timedelta(days=1)).date()

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

    await state.clear()

    await render_tasks(message, user_id, is_evening=True)


# ================================
# ✅ DONE
# ================================
@router.callback_query(lambda c: c.data.startswith("task_done_"))
async def task_done(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[-1])

    pool = await get_pool()
    async with pool.acquire() as conn:
        current_status = await conn.fetchval(
            "SELECT status FROM daily_tasks WHERE id=$1",
            task_id
        )

        new_status = "pending" if current_status == "done" else "done"

        await conn.execute(
            "UPDATE daily_tasks SET status=$1 WHERE id=$2",
            new_status,
            task_id
        )
    await callback.answer("✅")

    await render_tasks(
        callback.message,
        callback.from_user.id,
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

    await render_tasks(
        callback.message,
        callback.from_user.id,
        is_evening=True,
        edit=True
    )


# ================================
# 🧪 DEBUG
# ================================
@router.message()
async def debug_day_plan_all(message: types.Message):
    print("DAY_PLAN DEBUG:", repr(message.text))