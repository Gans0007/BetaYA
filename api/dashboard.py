from fastapi import APIRouter, Request
from api.telegram_auth import validate_telegram_data
from core.database import get_pool

router = APIRouter()


@router.post("/api/dashboard")
async def get_dashboard(request: Request):

    data = await request.json()
    init_data = data.get("initData")

    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        habits_rows = await conn.fetch("""

        SELECT id,name
        FROM habits
        WHERE user_id=$1
        AND is_active=true
        ORDER BY created_at

        """,user_id)

        habits=[]

        for h in habits_rows:

            confirmations = await conn.fetch("""

            SELECT DATE(datetime) as day
            FROM confirmations
            WHERE habit_id=$1
            AND user_id=$2
            AND datetime >= NOW() - INTERVAL '5 days'

            """,h["id"],user_id)

            days=[r["day"] for r in confirmations]

            series=[]

            for i in range(4,-1,-1):

                day=(datetime.utcnow()-timedelta(days=i)).date()

                if day in days:
                    series.append(1)
                else:
                    series.append(0)

            habits.append({
                "id":h["id"],
                "name":h["name"],
                "series":series
            })

    return {"habits":habits}