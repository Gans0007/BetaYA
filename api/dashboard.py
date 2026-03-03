from fastapi import APIRouter, Request, HTTPException
from api.main import validate_telegram_data, app

router = APIRouter()

LEAGUE_THRESHOLDS = [
    (6000, "Созидатель"),
    (5200, "Непоколебимый"),
    (4000, "Лидер примера"),
    (2500, "Железный характер"),
    (1400, "Ответственный"),
    (700,  "Ученик дисциплины"),
    (300,  "Новичок"),
    (100,  "Сомневающийся"),
    (0,    "Безответственный"),
]

def calc_league(xp_value: float) -> str:
    for threshold, name in LEAGUE_THRESHOLDS:
        if xp_value >= threshold:
            return name
    return "Безответственный"


@router.post("/api/dashboard")
async def get_dashboard(request: Request):
    data = await request.json()
    init_data = data.get("initData")

    if not init_data:
        raise HTTPException(status_code=400, detail="initData missing")

    user_id = validate_telegram_data(init_data)

    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT current_streak, COALESCE(xp, 0) as xp
            FROM user_stats
            WHERE user_id = $1
            """,
            user_id
        )

    if not row:
        return {"telegram_user_id": user_id, "db_row": None}

    current_streak = row["current_streak"]
    xp = float(row["xp"] or 0)
    league = calc_league(xp)

    return {
        "telegram_user_id": user_id,
        "db_row": {
            "current_streak": current_streak,
            "xp": int(round(xp)),
            "league": league
        }
    }