import sqlite3
from config import DB_PATH
from aiogram import Bot

async def complete_challenge(habit_id: int, user_id: int, bot: Bot):
    with sqlite3.connect(DB_PATH) as conn:
        # Получаем данные о челлендже ДО удаления
        cursor = conn.execute("SELECT name, done_days, days FROM habits WHERE id = ? AND user_id = ?", (habit_id, user_id))
        row = cursor.fetchone()
        if not row:
            return  # Если привычка уже удалена, ничего не делаем

        name, done_days, total_days = row

        # Увеличиваем счётчик завершённых челленджей
        conn.execute("""
            UPDATE users
            SET finished_challenges = finished_challenges + 1
            WHERE user_id = ?
        """, (user_id,))

        # Удаляем привычку
        conn.execute("DELETE FROM habits WHERE id = ? AND user_id = ?", (habit_id, user_id))

    # 📢 Уведомление сразу в чат
    await bot.send_message(
        user_id,
        f"🏆 <b>Челлендж «{name}» завершён!</b>\n\n"
        f"<b>{done_days} из {total_days} дней</b> выполнено.\n"
        f"Теперь ты можешь взять новый вызов 💪",
        parse_mode="HTML"
    )
