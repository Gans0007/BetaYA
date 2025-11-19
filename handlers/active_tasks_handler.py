from aiogram import Router, types, F
from database import get_pool

from services.habit_view_service import send_habit_card, build_active_list

router = Router()


# =====================================================
# 🔹 Показ активных привычек (message)
# =====================================================
@router.message(lambda m: m.text == "📋 Активные задания")
async def show_active_tasks(message: types.Message):
    user_id = message.from_user.id

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
            ORDER BY h.is_challenge DESC, h.created_at DESC
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



@router.callback_query(F.data == "back_from_card")
async def back_from_card(callback: types.CallbackQuery):
    user_id = callback.from_user.id

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
            ORDER BY h.is_challenge DESC, h.created_at DESC
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
async def back_to_active_list(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    text, kb, rows = await build_active_list(user_id)

    if not rows:
        await callback.message.edit_text("😴 У тебя пока нет активных привычек или челленджей.")
    else:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)

    await callback.answer()
