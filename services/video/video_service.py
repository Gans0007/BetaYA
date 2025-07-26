import logging
from repositories.video.video_repo import (
    save_pending_video,
    get_pending_videos,
    get_pending_video_by_id,
    delete_video,
    approve_video,
    count_pending_videos_by_user,
)
from services.monetization.reward_service import add_reward

logger = logging.getLogger(__name__)

# Пользователь начинает загрузку видео
async def start_video_upload(user_id: int):
    pending_count = await count_pending_videos_by_user(user_id)
    return pending_count


# Сохраняем загруженное видео
async def submit_video_link(user_id: int, video_url: str):
    await save_pending_video(user_id=user_id, video_link=video_url)


# Возвращаем список видео для админа
async def list_pending_videos():
    return await get_pending_videos()


# Админ отклоняет видео
async def reject_video(video_id: int, bot):
    video = await get_pending_video_by_id(video_id)
    if video:
        try:
            await bot.send_message(
                video["user_id"],
                "❌ Ваше видео было отклонено администратором. Попробуйте загрузить другой вариант."
            )
        except Exception as e:
            logger.error(f"[VIDEO] ❌ Ошибка при отправке уведомления об отклонении: {e}")

    await delete_video(video_id)


# Админ одобряет видео
async def approve_video_and_reward(video_id: int, admin_id: int, bot):
    await approve_video(video_id)
    video = await get_pending_video_by_id(video_id)
    if not video:
        return

    user_id = video["user_id"]
    logger.info(f"[ADMIN] ✅ {admin_id} одобрил видео {video_id} пользователя {user_id}")

    # Начисляем награду
    await add_reward(user_id=user_id, amount=0.10, reason="Видео одобрено", reward_type="usdt")

    # Уведомления пользователю
    try:
        await bot.send_message(user_id, "✅ Ваше видео было одобрено администратором!")
        await bot.send_message(
            user_id,
            "Тебе благодарность от YA \n\n⭐ <b>+3 XP</b> за старание\n\n💸 <b>+0.10 USDT</b> за вклад в комьюнити!",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"[VIDEO] ❌ Ошибка при отправке уведомлений пользователю {user_id}: {e}")
