import aiosqlite
from config import DB_PATH
from utils.timezones import get_current_time
from services.users.xp_service import add_xp

async def save_pending_video(user_id: int, video_link: str):
    submitted_at = get_current_time().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO pending_videos (user_id, video_link, submitted_at)
            VALUES (?, ?, ?)
        """, (user_id, video_link, submitted_at))
        await db.commit()

async def get_pending_videos():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT id, user_id, video_link, submitted_at, approved
            FROM pending_videos
            WHERE approved = 0
        """)
        rows = await cursor.fetchall()
        await cursor.close()
        return rows

#посчитать в обработке видео пользователю
async def count_pending_videos_by_user(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT COUNT(*) FROM pending_videos
            WHERE user_id = ? AND approved = 0
        """, (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else 0

async def delete_video(video_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM pending_videos WHERE id = ?", (video_id,))
        await db.commit()

async def approve_video(video_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        # Обновляем статус
        await db.execute("UPDATE pending_videos SET approved = 1 WHERE id = ?", (video_id,))

        # Получаем user_id для начисления XP
        cursor = await db.execute("SELECT user_id FROM pending_videos WHERE id = ?", (video_id,))
        row = await cursor.fetchone()
        if row:
            user_id = row[0]

            # Начисляем 3 XP
            await add_xp(user_id, 3, "Одобрено видео", conn=db)

        await db.commit()


#получить данные одного конкретного видео по video_id
async def get_pending_video_by_id(video_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT id, user_id, video_link, submitted_at, approved
            FROM pending_videos
            WHERE id = ?
        """, (video_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
