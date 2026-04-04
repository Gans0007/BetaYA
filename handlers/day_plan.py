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
async def render_tasks(message: types.Message, user_id: int, date, is_evening: bool):
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

    if not tasks:
        await message.answer(
            "📋 Нет задач\n\nДобавь первую задачу 🔥"
        )
        return

    text = "📋 <b>Твои задачи:</b>\n\n"
    keyboard = []

    for i, task in enumerate(tasks, start=1):
        status_icon = {
            "pending": "⏳",
            "done": "✅",
            "failed": "❌"
        }.get(task["status"], "⏳")

        text += f"{i}. {task['text']} — {status_icon}\n"

        if is_evening:
            row = [
                InlineKeyboardButton(
                    text="🗑",
                    callback_data=f"task_delete_{task['id']}"
                )
            ]
        else:
            row = [
                InlineKeyboardButton(
                    text="✅",
                    callback_data=f"task_done_{task['id']}"
                ),
                InlineKeyboardButton(
                    text="❌",
                    callback_data=f"task_fail_{task['id']}"
                )
            ]

        keyboard.append(row)

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(text, parse_mode="HTML", reply_markup=markup)


# ================================
# 📋 ОТКРЫТИЕ ПЛАНА (ГЛАВНОЕ)
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

    # 🌙 ВЕЧЕР (создание задач)
    if 20 <= hour < 23:
        tomorrow = (now + timedelta(days=1)).date()

        await render_tasks(message, user_id, tomorrow, is_evening=True)

        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="➕ Добавить задачу")],
                [types.KeyboardButton(text="⬅ Назад")]
            ],
            resize_keyboard=True
        )

        await message.answer(
            "➕ Добавь или удали задачи",
            reply_markup=keyboard
        )
        return

    # 🌅 ДЕНЬ (выполнение)
    today = now.date()

    await render_tasks(message, user_id, today, is_evening=False)


# ================================
# ➕ НАЧАТЬ ДОБАВЛЕНИЕ
# ================================
@router.message(lambda m: m.text and "Добавить задачу" in m.text)
async def add_task_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    pool = await get_pool()
    async with pool.acquire() as conn:
        tz_name = await conn.fetchval(
            "SELECT timezone FROM users WHERE user_id=$1",
            user_id
        )

        access_until = await conn.fetchval(
            "SELECT access_until FROM users WHERE user_id=$1",
            user_id
        )

    tz_name = tz_name or "Europe/Kyiv"
    now = datetime.now(ZoneInfo(tz_name))
    hour = now.hour

    if not (20 <= hour < 23):
        await message.answer("⛔ Добавлять задачи можно только вечером")
        return

    tomorrow = (now + timedelta(days=1)).date()

    async with pool.acquire() as conn:
        count = await conn.fetchval(
            """
            SELECT COUNT(*) FROM daily_tasks
            WHERE user_id=$1 
            AND planned_for_date=$2 
            AND is_deleted=FALSE
            """,
            user_id,
            tomorrow
        )

    limit = 5 if access_until and access_until > now else 2

    if count >= limit:
        await message.answer(
            "🚫 Лимит задач достигнут\n\n"
            "🔓 Купи доступ для увеличения лимита"
        )
        return

    await state.set_state(AddTaskFSM.waiting_for_text)
    await message.answer("✍️ Введи задачу:")


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

    await message.answer(
        f"✅ Задача добавлена:\n{text}\n\n"
        "📋 Нажми 'План на завтра' чтобы увидеть список"
    )


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

    await callback.answer("✅ Выполнено")
    await callback.message.delete()


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

    await callback.answer("❌ Провалено")
    await callback.message.delete()


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
    await callback.message.delete()