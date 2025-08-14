from db.db import database
from aiogram import Bot


async def complete_challenge(habit_id: int, user_id: int, bot: Bot):
    # Получаем данные о челлендже до удаления
    row = await database.fetch_one("""
        SELECT name, description, days, done_days
        FROM habits
        WHERE id = :habit_id AND user_id = :user_id
    """, {"habit_id": habit_id, "user_id": user_id})

    if not row:
        return  # Если привычка уже удалена

    name = row["name"]
    description = row["description"]
    done_days = row["done_days"]
    total_days = row["days"]

    # 1. Сохраняем в completed_challenges
    await database.execute("""
        INSERT INTO completed_challenges (user_id, name, description, days, done_days, completed_at)
        VALUES (:user_id, :name, :description, :days, :done_days, CURRENT_TIMESTAMP)
    """, {
        "user_id": user_id,
        "name": name,
        "description": description,
        "days": total_days,
        "done_days": done_days,
    })

    # 2. Увеличиваем счётчик завершённых челленджей
    await database.execute("""
        UPDATE users
        SET finished_challenges = finished_challenges + 1
        WHERE user_id = :user_id
    """, {"user_id": user_id})

    # 3. Удаляем привычку
    await database.execute("""
        DELETE FROM habits
        WHERE id = :habit_id AND user_id = :user_id
    """, {"habit_id": habit_id, "user_id": user_id})

    # 4. Сообщение пользователю
    await bot.send_message(
        user_id,
        f"🏆 <b>Челлендж «{name}» завершён!</b>\n\n"
        f"<b>{done_days} из {total_days} дней</b> выполнено.\n"
        f"Теперь ты можешь взять новый вызов 💪",
        parse_mode="HTML"
    )
