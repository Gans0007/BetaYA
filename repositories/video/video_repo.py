import aiosqlite
from config import DB_PATH

async def save_pending_video(user_id: int, video_link: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO pending_videos (user_id, video_link)
            VALUES (?, ?)
        """, (user_id, video_link))
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
        await db.execute("UPDATE pending_videos SET approved = 1 WHERE id = ?", (video_id,))
        await db.commit()
