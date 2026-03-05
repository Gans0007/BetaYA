from fastapi import APIRouter, Request
from api.telegram_auth import validate_telegram_data
from core.database import get_pool

router = APIRouter()


@router.post("/api/dashboard")
async def get_dashboard(request: Request):

    # --------------------------
    # 1) Читаем JSON body
    # --------------------------
    try:
        data = await request.json()
    except:
        data = {}

    init_data = data.get("initData")

    if not init_data:
        return {
            "telegram_user_id": None,
            "streak": 0,
            "xp": 0,
            "league": "Безответственный",
            "habits": [],
            "debug": "initData missing"
        }

    # --------------------------
    # 2) Достаём Telegram user_id
    # --------------------------
    user_id = validate_telegram_data(init_data)

    pool = await get_pool()

    async with pool.acquire() as conn:

        # --------------------------
        # 3) USER STATS (как раньше)
        # --------------------------
        row = await conn.fetchrow(
            """
            SELECT
                COALESCE(current_streak,0) as current_streak,
                COALESCE(xp,0) as xp,
                COALESCE(league,'Безответственный') as league
            FROM user_stats
            WHERE user_id = $1
            """,
            user_id
        )

        # --------------------------
        # 4) HABITS + SERIES(5 дней) из confirmations (1 запрос)
        #
        # series: 0/1 по последним 5 дням (4 дня назад ... сегодня)
        # 1 = было хотя бы 1 подтверждение в этот день
        # --------------------------
        rows = await conn.fetch(
            """
            WITH days AS (
                -- 5 дней: (сегодня-4) ... (сегодня)
                SELECT (CURRENT_DATE - offs)::date AS day, offs
                FROM generate_series(4, 0, -1) AS offs
            ),
            h AS (
                SELECT id, name, created_at
                FROM habits
                WHERE user_id = $1
                  AND is_active = TRUE
            ),
            c AS (
                SELECT
                    habit_id,
                    DATE(datetime) AS day,
                    COUNT(*) AS cnt
                FROM confirmations
                WHERE user_id = $1
                  AND datetime >= (CURRENT_DATE - 4)
                  AND datetime <  (CURRENT_DATE + 1)
                GROUP BY habit_id, DATE(datetime)
            )
            SELECT
                h.id AS habit_id,
                h.name AS habit_name,
                d.day AS day,
                COALESCE(c.cnt, 0) AS cnt
            FROM h
            CROSS JOIN days d
            LEFT JOIN c
                ON c.habit_id = h.id
               AND c.day = d.day
            ORDER BY h.created_at, h.id, d.day
            """,
            user_id
        )

    # --------------------------
    # 5) Собираем habits -> series[5]
    # --------------------------
    habits_map = {}
    for r in rows:
        hid = r["habit_id"]
        if hid not in habits_map:
            habits_map[hid] = {
                "id": hid,
                "name": r["habit_name"],
                "series": []
            }

        # 0/1 по дню
        habits_map[hid]["series"].append(1 if r["cnt"] > 0 else 0)

    habits = list(habits_map.values())

    return {
        "telegram_user_id": user_id,

        # оставляем как в “рабочей” версии — чтобы фронт не ломался
        "streak": row["current_streak"] if row else 0,
        "xp": float(row["xp"]) if row else 0,
        "league": row["league"] if row else "Безответственный",

        # теперь habits уже с series (для мини-графика)
        "habits": habits
    }