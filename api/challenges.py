from fastapi import APIRouter, Request
from data.challenges_data import CHALLENGES, CHALLENGE_LEVELS, LEVEL_UNLOCKS
from repositories.challenge_repository import get_completed_challenges, get_user_total_stars
from core.database import get_pool

import json
from urllib.parse import parse_qs

router = APIRouter()


@router.post("/api/challenges")
async def get_challenges(request: Request):
    data = await request.json()
    init_data = data.get("initData")

    user_id = 0

    if init_data:
        try:
            parsed = parse_qs(init_data)
            if "user" in parsed:
                user_json = parsed["user"][0]
                user_data = json.loads(user_json)
                user_id = user_data.get("id", 0)
        except Exception as e:
            print("INIT DATA PARSE ERROR:", e)

    print("🔥 USER ID:", user_id)

    # ⭐ звезды
    completed_rows = await get_completed_challenges(user_id)
    completed_map = {
        row["challenge_id"]: row["repeat_count"]
        for row in completed_rows
    }

    # ⭐ total stars
    user_stars = await get_user_total_stars(user_id) or 0

    # 🔥 habits
    pool = await get_pool()
    async with pool.acquire() as conn:
        habit_rows = await conn.fetch("""
            SELECT challenge_id, done_days, days
            FROM habits
            WHERE user_id = $1
              AND is_challenge = TRUE
              AND is_active = TRUE
        """, user_id)

    habit_map = {
        row["challenge_id"]: row
        for row in habit_rows
        if row["challenge_id"]
    }

    modules = []

    for level_key, challenges in CHALLENGES.items():

        required_stars = LEVEL_UNLOCKS.get(level_key, 0)
        is_unlocked = user_stars >= required_stars

        module = {
            "level": level_key,
            "level_name": CHALLENGE_LEVELS["ru"][level_key],
            "required_stars": required_stars,
            "is_unlocked": is_unlocked,
            "challenges": []
        }

        # 🔒 если закрыт — не добавляем челленджи
        if not is_unlocked:
            modules.append(module)
            continue

        for ch in challenges:
            ch_id, title, texts, _ = ch

            repeat_count = completed_map.get(ch_id, 0)

            current_section = min(repeat_count + 1, 3)

            base_days_map = {1: 7, 2: 10, 3: 13}

            active = habit_map.get(ch_id)

            if active:
                done_days = active["done_days"] or 0
                total_days = active["days"] or base_days_map[current_section]
                is_active = True
            else:
                done_days = 0
                total_days = base_days_map[current_section]
                is_active = False

            module["challenges"].append({
                "id": ch_id,
                "title": title,
                "current_section": {
                    "section": current_section,
                    "days": total_days,
                    "stars": current_section
                },
                "progress": {
                    "done_days": done_days,
                    "is_active": is_active
                }
            })

        modules.append(module)

    return {"modules": modules}