from db.db import database
from aiogram import Bot


async def complete_challenge(habit_id: int, user_id: int, bot: Bot):
    # Получаем данные о челлендже до удаления
    row = await database.fetch_one("""
        SELECT name, done_days, days FROM habits
        WHERE id = :habit_id AND user_id = :user_id
    """, {"habit_id": habit_id, "user_id": user_id})

    if not row:
        return  # Если привычка уже удалена

    name, done_days, total_days = row["name"], row["done_days"], row["days"]

    # Увеличиваем счётчик завершённых челленджей
    await database.execute("""
        UPDATE users
        SET finished_challenges = finished_challenges + 1
        WHERE user_id = :user_id
    """, {"user_id": user_id})

    # Удаляем привычку
    await database.execute("""
        DELETE FROM habits
        WHERE id = :habit_id AND user_id = :user_id
    """, {"habit_id": habit_id, "user_id": user_id})

    # 📢 Уведомление
    await bot.send_message(
        user_id,
        f"🏆 <b>Челлендж «{name}» завершён!</b>\n\n"
        f"<b>{done_days} из {total_days} дней</b> выполнено.\n"
        f"Теперь ты можешь взять новый вызов 💪",
        parse_mode="HTML"
    )
