from fastapi import APIRouter, Request
from data.challenges_data import CHALLENGES, CHALLENGE_LEVELS

from repositories.challenge_repository import (
    get_completed_challenges,
    get_active_challenges
)

router = APIRouter()


@router.post("/api/challenges")
async def get_challenges(request: Request):

    data = await request.json()
    init_data = data.get("initData")

    user_id = 0  # пока упрощенно

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

            # 🔥 проверяем активность
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