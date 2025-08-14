from db.db import database
from aiogram import Bot

# Словарь текстов достижений
ACHIEVEMENTS_TEXTS = {
    "first_habit": (
        "🏅 Новое достижение: \"Первый шаг\"\n"
        "Ты создал свою первую привычку!\n"
        "С этого момента начинается твой путь к новой версии себя. 🚀"
    ),
    "first_challenge": (
        "🔥 Новое достижение: \"Вызов принят\"\n"
        "Ты взял свой первый челлендж!\n"
        "Теперь дисциплина проверит тебя на прочность. 💪"
    ),
    "streak_3": (
        "🏆 Новое достижение: \"Триумф 3\"\n"
        "Ты подтвердил привычку 3 дня подряд!\n"
        "Начало стабильности положено — продолжай!\n\n"
        "Больше мотивации и поддержки в полной версии. Позволь мне быть твоей поддержкой!"
    )
}

async def show_achievement(bot: Bot, user_id: int, code: str):
    """
    Выдаёт достижение только один раз.
    """
    text = ACHIEVEMENTS_TEXTS.get(code)
    if not text:
        return

    # Проверяем, есть ли уже такое достижение
    row = await database.fetch_one(
        "SELECT 1 FROM achievements WHERE user_id = :user_id AND code = :code",
        {"user_id": user_id, "code": code}
    )
    if row:
        return  # уже выдавали

    # Сохраняем факт выдачи
    await database.execute(
        "INSERT INTO achievements (user_id, code) VALUES (:user_id, :code)",
        {"user_id": user_id, "code": code}
    )

    # Отправляем сообщение
    await bot.send_message(user_id, text)