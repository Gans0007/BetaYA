from fastapi import APIRouter, Request
from api.telegram_auth import validate_telegram_data
from core.database import get_pool

router = APIRouter()


@router.post("/api/leaderboard")
async def get_leaderboard(request: Request):

    try:
        data = await request.json()
    except:
        data = {}

    init_data = data.get("initData")

    if not init_data:
        return {"leaders": []}

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        # ТОП 10
        rows = await conn.fetch("""

        SELECT
            u.last_global_rank,
            COALESCE(u.username, u.first_name, 'Unknown') as username,
            s.xp

        FROM users u
        JOIN user_stats s ON s.user_id = u.user_id

        WHERE u.last_global_rank IS NOT NULL

        ORDER BY u.last_global_rank
        LIMIT 10

        """)

        # МОЕ МЕСТО
        my = await conn.fetchrow("""

        SELECT
            u.last_global_rank,
            COALESCE(u.username, u.first_name, 'You') as username,
            s.xp

        FROM users u
        JOIN user_stats s ON s.user_id = u.user_id

        WHERE u.user_id=$1

        """, user_id)


    leaders = []

    for r in rows:

        leaders.append({
            "rank": r["last_global_rank"],
            "username": r["username"],
            "xp": int(r["xp"])
        })


    return {

        "leaders": leaders,

        "my_rank": my["last_global_rank"] if my else None,
        "my_xp": int(my["xp"]) if my else 0,
        "my_username": my["username"] if my else None

    }