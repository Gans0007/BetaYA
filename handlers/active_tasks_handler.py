from aiogram import Router, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.database import get_pool

from services.habit_view_service import send_habit_card, build_active_list
from services.user_stats_service import increment_finished_habits
from services.fsm_ui import clear_fsm_ui
from aiogram.fsm.context import FSMContext

router = Router()

import logging
logger = logging.getLogger(__name__)

# =====================================================
# 🔹 Показ активных привычек (message)
# =====================================================
@router.message(lambda m: m.text == "📋 Активные привычки")
async def show_active_tasks(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"👤 Пользователь {user_id} открыл список активных привычек.")

    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT h.id, h.name, h.description, h.days, h.done_days, h.is_challenge, h.difficulty,
                   (SELECT datetime FROM confirmations
                        WHERE habit_id = h.id
                        ORDER BY datetime DESC
                        LIMIT 1) AS last_date,
                   u.timezone
            FROM habits h
            JOIN users u ON u.user_id = h.user_id
            WHERE h.user_id = $1 AND h.is_active = TRUE
            ORDER BY h.created_at ASC
        """, user_id)

    # Нет активных привычек
    if not rows:
        await message.answer("😴 У тебя пока нет активных привычек или челленджей.")
        return

    # Если <= 2 — показываем карточки
    if len(rows) <= 2:
        for habit in rows:
            await send_habit_card(message.chat, habit, user_id)   # используем chat
        return

    # Если 3+ — показываем список
    text, kb, _ = await build_active_list(user_id)
    await message.answer(text, parse_mode="Markdown", reply_markup=kb)


# =====================================================
# 🔹 Показ карточки привычки (callback)
# =====================================================
@router.callback_query(F.data.startswith("habit_"))
async def show_habit_card(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    logger.info(f"👤 Пользователь {user_id} открыл карточку привычки ID={habit_id}.")

    pool = await get_pool()
    async with pool.acquire() as conn:
        habit = await conn.fetchrow("""
            SELECT h.id, h.name, h.description, h.days, h.done_days, h.is_challenge,
                   h.difficulty,
                   (SELECT datetime FROM confirmations
                        WHERE habit_id = h.id
                        ORDER BY datetime DESC
                        LIMIT 1) AS last_date,
                   u.timezone
            FROM habits h
            JOIN users u ON u.user_id = h.user_id
            WHERE h.id=$1 AND h.user_id=$2
        """, habit_id, user_id)

    if not habit:
        await callback.message.edit_text("❌ Привычка не найдена или уже завершена.")
        await callback.answer()
        return

    chat = callback.message.chat  # сохраняем chat до удаления

    await callback.message.delete()

    # Отправляем карточку в чат (правильно)
    await send_habit_card(chat, habit, user_id)

    await callback.answer()


# =====================================================
# 🔹 Возврат с карточки к списку/карточкам
# =====================================================
@router.callback_query(F.data == "back_from_card")
async def back_from_card(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"👤 Пользователь {callback.from_user.id} вернулся из карточки назад.")

    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT h.id, h.name, h.description, h.days, h.done_days, h.is_challenge,
                   h.difficulty,
                   (SELECT datetime FROM confirmations
                        WHERE habit_id = h.id
                        ORDER BY datetime DESC LIMIT 1) AS last_date,
                   u.timezone
            FROM habits h
            JOIN users u ON u.user_id=h.user_id
            WHERE h.user_id=$1 AND h.is_active=TRUE
            ORDER BY h.created_at ASC
        """, user_id)

    # 🔹 0 привычек
    if not rows:
        await callback.message.edit_text("😴 У тебя пока нет активных привычек или челленджей.")
        await callback.answer()
        return

    # 🔹 1–2 привычки → показываем карточки
    if len(rows) <= 2:
        await callback.message.delete()
        for h in rows:
            await send_habit_card(callback.message.chat, h, user_id)
        await callback.answer()
        return

    # 🔹 3+ привычек → показываем список
    text, kb, _ = await build_active_list(user_id)
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()


# =====================================================
# 🔹 Возврат к списку (callback)
# =====================================================
@router.callback_query(F.data == "show_active_list")
async def back_to_active_list(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    await clear_fsm_ui(
        state=state,
        bot=callback.bot,
        chat_id=callback.message.chat.id
    )

    await state.clear()   # ✅ ВНУТРИ функции

    logger.info(f"👤 Пользователь {callback.from_user.id} запросил список привычек.")

    text, kb, rows = await build_active_list(user_id)

    if not rows:
        await callback.message.edit_text("😴 У тебя пока нет активных привычек.")
    else:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)

    await callback.answer()

# ================================
# 🔥 1) Запрос подтверждения удаления привычки
#     Срабатывает по кнопке ask_delete_<id>
# ================================
@router.callback_query(F.data.startswith("ask_delete_"))
async def ask_delete(callback: types.CallbackQuery):
    # Получаем id привычки
    habit_id = int(callback.data.split("_")[2])
    logger.info(f"🗑 Пользователь {callback.from_user.id} запросил удаление привычки ID={habit_id}.")

    # Клавиатура: Да / Отмена
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Да, удалить", callback_data=f"delete_habit_{habit_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="dismiss_delete")]
        ]
    )

    # Показываем вопрос
    await callback.message.edit_text(
        "❗ Ты точно хочешь удалить эту привычку?",
        reply_markup=kb
    )

    await callback.answer()


# ================================
# 🔥 2) Удаление привычки
#     Срабатывает по кнопке delete_habit_<id>
# ================================
@router.callback_query(F.data.startswith("delete_habit_"))
async def delete_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    logger.info(f"❗ Пользователь {user_id} подтвердил удаление привычки ID={habit_id}.")

    pool = await get_pool()

    async with pool.acquire() as conn:

        # 🟦 1. Считаем количество привычек ДО удаления
        before_rows = await conn.fetch("""
            SELECT id FROM habits
            WHERE user_id=$1 AND is_active=TRUE
        """, user_id)
        before_count = len(before_rows)

        # ---------------------------------------------------
        # 🟦 2. Удаляем привычку + её подтверждения
        # ---------------------------------------------------
        await conn.execute("DELETE FROM confirmations WHERE habit_id=$1", habit_id)
        await conn.execute("DELETE FROM habits WHERE id=$1 AND user_id=$2", habit_id, user_id)

        # ---------------------------------------------------
        # 🟦 3. Грузим привычки ПОСЛЕ удаления
        # ---------------------------------------------------
        habits = await conn.fetch("""
            SELECT h.id, h.name, h.description, h.days, h.done_days,
                   h.is_challenge, h.difficulty,
                   (SELECT datetime FROM confirmations
                        WHERE habit_id=h.id
                        ORDER BY datetime DESC LIMIT 1) AS last_date,
                   u.timezone
            FROM habits h
            JOIN users u ON u.user_id=h.user_id
            WHERE h.user_id=$1 AND h.is_active=TRUE
            ORDER BY h.created_at ASC
        """, user_id)

    # ---------------------------------------------------
    # 🟥 0 привычек осталось
    # ---------------------------------------------------
    if before_count == 1:
        await callback.message.edit_text(
            "🗑 Привычка удалена.\n\n😴 Больше нет активных привычек."
        )
        await callback.answer()
        return

    # ---------------------------------------------------
    # 🟧 Было 2 → стало 1 → показываем карточка удалена
    # ---------------------------------------------------
    if before_count == 2:
        await callback.message.edit_text(
            "🗑 Привычка удалена."
        )
        await callback.answer()
        return

    # ---------------------------------------------------
    # 🟨 Было 3 → стало 2 → показываем 2 карточки
    # ---------------------------------------------------
    if before_count == 3:
        await callback.message.delete()
        for h in habits:
            await send_habit_card(callback.message.chat, h, user_id)
        await callback.answer()
        return

    # ---------------------------------------------------
    # 🟩 Было 4+ → показываем список
    # ---------------------------------------------------
    if before_count >= 4:
        try:
            await callback.message.delete()
        except:
            pass

        text, kb, _ = await build_active_list(user_id)
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=kb)
        await callback.answer()
        return


# ================================
# 🔥 3) Отмена удаления привычки
# ================================
@router.callback_query(F.data == "dismiss_delete")
async def dismiss_delete(callback: types.CallbackQuery):
    logger.info(f"❌ Пользователь {callback.from_user.id} отменил удаление привычки.")
    # Возвращаем обычное сообщение
    await callback.message.edit_text("Отменено ❎")
    await callback.answer()


# ================================
# 🔁 Запрос подтверждения продления
# ================================

@router.callback_query(
    F.data.startswith("extend_")
    & ~F.data.startswith("extend_confirm_")
    & ~F.data.startswith("extend_cancel_")
)
async def ask_extend_habit(callback: types.CallbackQuery):

    habit_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    logger.info(f"[EXTEND_ASK] user={user_id} habit_id={habit_id}")

    pool = await get_pool()
    async with pool.acquire() as conn:
        habit = await conn.fetchrow("""
            SELECT name
            FROM habits
            WHERE id=$1 AND user_id=$2
        """, habit_id, user_id)

    if not habit:
        await callback.answer("❌ Привычка не найдена.", show_alert=True)
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ Да, продлить на 7 дней",
                callback_data=f"extend_confirm_{habit_id}"
            )],
            [InlineKeyboardButton(
                text="❌ Нет",
                callback_data=f"extend_cancel_{habit_id}"
            )]
        ]
    )

    await callback.message.edit_text(
        f"🔁 *Продлить привычку «{habit['name']}» на 7 дней?*",
        parse_mode="Markdown",
        reply_markup=kb
    )

    await callback.answer()


# ================================
# ✅ Подтверждение продления
# ================================
@router.callback_query(F.data.startswith("extend_confirm_"))
async def confirm_extend_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    logger.info(f"[EXTEND_CONFIRM] user={user_id} habit_id={habit_id}")

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE habits
            SET days = days + 7
            WHERE id=$1 AND user_id=$2
        """, habit_id, user_id)

        habit = await conn.fetchrow("""
            SELECT h.id, h.name, h.description, h.days, h.done_days, h.is_challenge,
                   h.difficulty,
                   (SELECT datetime FROM confirmations
                        WHERE habit_id=h.id
                        ORDER BY datetime DESC LIMIT 1) AS last_date,
                   u.timezone
            FROM habits h
            JOIN users u ON u.user_id=h.user_id
            WHERE h.id=$1 AND h.user_id=$2
        """, habit_id, user_id)

    await callback.answer("🔁 Привычка продлена на 7 дней", show_alert=True)

    try:
        await callback.message.delete()
    except:
        pass

    await send_habit_card(callback.message.chat, habit, user_id)


# ================================
# ❌ Отмена продления
# ================================
@router.callback_query(F.data.startswith("extend_cancel_"))
async def cancel_extend_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    logger.info(f"[EXTEND_CANCEL] user={user_id} habit_id={habit_id}")

    pool = await get_pool()
    async with pool.acquire() as conn:
        habit = await conn.fetchrow("""
            SELECT h.id, h.name, h.description, h.days, h.done_days, h.is_challenge,
                   h.difficulty,
                   (SELECT datetime FROM confirmations
                        WHERE habit_id=h.id
                        ORDER BY datetime DESC LIMIT 1) AS last_date,
                   u.timezone
            FROM habits h
            JOIN users u ON u.user_id=h.user_id
            WHERE h.id=$1 AND h.user_id=$2
        """, habit_id, user_id)

    try:
        await callback.message.delete()
    except:
        pass

    await send_habit_card(callback.message.chat, habit, user_id)
    await callback.answer()



# ================================
# ✅ Вопрос о завершении привычки
# ================================
@router.callback_query(
    F.data.startswith("finish_")
    & ~F.data.startswith("finish_confirm_")
    & ~F.data.startswith("finish_cancel_")
)
async def ask_finish_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    logger.info(f"[FINISH_ASK] user={user_id} habit_id={habit_id}")

    pool = await get_pool()
    async with pool.acquire() as conn:
        habit = await conn.fetchrow("""
            SELECT name
            FROM habits
            WHERE id=$1 AND user_id=$2
        """, habit_id, user_id)

    if not habit:
        await callback.answer("❌ Привычка не найдена.", show_alert=True)
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ Да, завершить",
                callback_data=f"finish_confirm_{habit_id}"
            )],
            [InlineKeyboardButton(
                text="❌ Нет",
                callback_data=f"finish_cancel_{habit_id}"
            )]
        ]
    )

    await callback.message.edit_text(
        f"🏁 *Завершить привычку «{habit['name']}»?*",
        parse_mode="Markdown",
        reply_markup=kb
    )

    await callback.answer()

# ================================
# ✅ Завершить привычку
# ================================
@router.callback_query(F.data.startswith("finish_confirm_"))
async def confirm_finish_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    logger.info(f"[FINISH_CONFIRM] user={user_id} habit_id={habit_id}")

    pool = await get_pool()
    async with pool.acquire() as conn:
        habit = await conn.fetchrow("""
            SELECT name
            FROM habits
            WHERE id=$1 AND user_id=$2
        """, habit_id, user_id)

        if not habit:
            await callback.answer("❌ Привычка уже завершена.", show_alert=True)
            return

        habit_name = habit["name"]

        await increment_finished_habits(conn, user_id)

        await conn.execute("DELETE FROM confirmations WHERE habit_id=$1", habit_id)
        await conn.execute("DELETE FROM habits WHERE id=$1 AND user_id=$2", habit_id, user_id)

    await callback.answer(
        f"🎉 Привычка «{habit_name}» завершена!",
        show_alert=True
    )

    try:
        await callback.message.delete()
    except:
        pass

    text, kb, rows = await build_active_list(user_id)

    if not rows:
        await callback.message.answer(
            "🏁 *Привычка завершена!*\n\n😴 Активных привычек больше нет.",
            parse_mode="Markdown"
        )
    else:
        await callback.message.answer(
            "🏁 *Привычка завершена!*\n\nПродолжаем движение дальше 💪",
            parse_mode="Markdown",
            reply_markup=kb
        )



# ================================
# ✅ Отмена завершения привычки
# ================================
@router.callback_query(F.data.startswith("finish_cancel_"))
async def cancel_finish_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    logger.info(f"[FINISH_CANCEL] user={user_id} habit_id={habit_id}")

    pool = await get_pool()
    async with pool.acquire() as conn:
        habit = await conn.fetchrow("""
            SELECT h.id, h.name, h.description, h.days, h.done_days, h.is_challenge,
                   h.difficulty,
                   (SELECT datetime FROM confirmations
                        WHERE habit_id=h.id
                        ORDER BY datetime DESC LIMIT 1) AS last_date,
                   u.timezone
            FROM habits h
            JOIN users u ON u.user_id=h.user_id
            WHERE h.id=$1 AND h.user_id=$2
        """, habit_id, user_id)

    try:
        await callback.message.delete()
    except:
        pass

    if habit:
        await send_habit_card(callback.message.chat, habit, user_id)

    await callback.answer()
