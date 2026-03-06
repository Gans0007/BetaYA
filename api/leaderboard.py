from fastapi import APIRouter
from core.database import get_pool

router = APIRouter()

@router.get("/api/leaderboard")
async def get_leaderboard():

    pool = await get_pool()

    async with pool.acquire() as conn:

        rows = await conn.fetch("""

        SELECT
            u.username,
            s.xp

        FROM user_stats s

        JOIN users u
            ON u.user_id = s.user_id

        ORDER BY s.xp DESC
        LIMIT 10

        """)

    leaderboard = []

    rank = 1

    for r in rows:

        leaderboard.append({
            "rank": rank,
            "username": r["username"],
            "xp": int(r["xp"])
        })

        rank += 1

    return {"leaders": leaderboard}