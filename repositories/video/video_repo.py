from db.db import database
from utils.timezones import get_current_time
from services.monetization.reward_service import add_reward


async def save_pending_video(user_id: int, video_link: str):
    submitted_at = get_current_time().strftime("%Y-%m-%d %H:%M:%S")
    await database.execute("""
        INSERT INTO pending_videos (user_id, video_link, submitted_at)
        VALUES (:user_id, :video_link, :submitted_at)
    """, {
        "user_id": user_id,
        "video_link": video_link,
        "submitted_at": submitted_at
    })


async def get_pending_videos():
    rows = await database.fetch_all("""
        SELECT id, user_id, video_link, submitted_at, approved
        FROM pending_videos
        WHERE approved = FALSE
    """)
    return [dict(row) for row in rows]


async def count_pending_videos_by_user(user_id: int) -> int:
    result = await database.fetch_one("""
        SELECT COUNT(*) AS count
        FROM pending_videos
        WHERE user_id = :user_id AND approved = FALSE
    """, {"user_id": user_id})
    return result["count"] if result else 0


async def delete_video(video_id: int):
    await database.execute("DELETE FROM pending_videos WHERE id = :id", {"id": video_id})


async def approve_video(video_id: int):
    # Обновляем статус
    await database.execute("""
        UPDATE pending_videos SET approved = TRUE WHERE id = :id
    """, {"id": video_id})

    # Получаем user_id и начисляем XP
    result = await database.fetch_one("""
        SELECT user_id FROM pending_videos WHERE id = :id
    """, {"id": video_id})
    if result:
        await add_xp(result["user_id"], 3, "Одобрено видео")


async def get_pending_video_by_id(video_id: int) -> dict | None:
    row = await database.fetch_one("""
        SELECT id, user_id, video_link, submitted_at, approved
        FROM pending_videos
        WHERE id = :id
    """, {"id": video_id})
    return dict(row) if row else None
