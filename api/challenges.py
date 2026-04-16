from fastapi import APIRouter, Request
from data.challenges_data import CHALLENGES, CHALLENGE_LEVELS

from repositories.challenge_repository import (
    get_completed_challenges,
    get_active_challenges
)

import json
from urllib.parse import parse_qs

router = APIRouter()


@router.post("/api/challenges")
async def get_challenges(request: Request):

    data = await request.json()
    init_data = data.get("initData")

    # 🔥 ПРАВИЛЬНО ДОСТАЕМ user_id ИЗ TELEGRAM
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

    # ⭐ completed (звезды)
    completed_rows = await get_completed_challenges(user_id)
    completed_map = {
        row["challenge_id"]: row["repeat_count"]
        for row in completed_rows
    }

    # 🔥 active (прогресс)
    active_rows = await get_active_challenges(user_id)
    active_map = {
        row["challenge_id"]: row
        for row in active_rows
    }

    modules = []

    for level_key, challenges in CHALLENGES.items():

        module = {
            "level": level_key,
            "level_name": CHALLENGE_LEVELS["ru"][level_key],
            "challenges": []
        }

        for ch in challenges:
            ch_id, title, texts, _ = ch

            # ⭐ уровень через repeat_count
            repeat_count = completed_map.get(ch_id, 0)

            current_section = repeat_count + 1
            if current_section > 3:
                current_section = 3

            base_days_map = {1: 7, 2: 10, 3: 13}

            # 🔥 активный челлендж
            active = active_map.get(ch_id)

            if active:
                done_days = active.get("done_days", 0)
                total_days = active.get("days", base_days_map[current_section])
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
                    "stars": current_section,
                    "text": texts.get(current_section, "")
                },

                "progress": {
                    "done_days": done_days,
                    "is_active": is_active
                }
            })

        modules.append(module)

    return {
        "modules": modules
    }