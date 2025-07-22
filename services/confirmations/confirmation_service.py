# services/confirmations/confirmation_service.py

from aiogram import Bot
from aiogram.types import User
from config import PUBLIC_CHAT_ID
import random
from repositories.habits.habit_repo import get_progress_by_habit_id
from repositories.habits.habit_repo import increment_done_day
from handlers.rules_text import CONFIRMATION_CAPTIONS



from repositories.confirmations.confirmation_repo import (
    log_confirmation,
    was_confirmed_today,
    update_confirmation_file,
)

async def process_confirmation(
    user_id: int,
    habit_id: int,
    file_id: str | None,
    file_type: str | None,
    bot: Bot
) -> bool:
    """
    Обрабатывает подтверждение привычки:
    - Если уже было подтверждение сегодня — просто обновляет медиа
    - Если нет — увеличивает прогресс и логирует подтверждение

    Возвращает True, если прогресс увеличен, иначе False
    """
    if await was_confirmed_today(user_id, habit_id):
        await update_confirmation_file(user_id, habit_id, file_id, file_type)
        return False
    else:
        await increment_done_day(habit_id)
        await log_confirmation(user_id, habit_id, file_id, file_type, bot)
        return True

def get_display_name(user: User) -> str:
    return f"@{user.username}" if user.username else user.full_name

def get_random_caption(user: User, habit_name: str, done: int, total: int) -> str:
    display_name = get_display_name(user)
    done = int(done)
    total = int(total)
    percent = round((done / total) * 100) if total > 0 else 0

    return random.choice(CONFIRMATION_CAPTIONS).format(
        name=display_name,
        habit=habit_name,
        done=done,
        total=total,
        percent=percent
    )

async def send_to_public_chat(
    user: User,
    habit_id: int,
    file_id: str | None,
    file_type: str,
    bot: Bot
):
    """
    Отправляет подтверждение привычки в публичный канал с подписью.
    """
    progress = await get_progress_by_habit_id(habit_id)
    name = progress["name"]
    done = progress["done_days"]
    total = progress["days"]

    caption = get_random_caption(user, name, done, total)

    if file_type == "photo":
        await bot.send_photo(chat_id=PUBLIC_CHAT_ID, photo=file_id, caption=caption, parse_mode="HTML")
    elif file_type == "video":
        await bot.send_video(chat_id=PUBLIC_CHAT_ID, video=file_id, caption=caption, parse_mode="HTML")
    elif file_type == "video_note":
        await bot.send_video_note(chat_id=PUBLIC_CHAT_ID, video_note=file_id)
        await bot.send_message(chat_id=PUBLIC_CHAT_ID, text=caption, parse_mode="HTML")

