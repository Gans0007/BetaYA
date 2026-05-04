from fastapi import APIRouter, Request
from data.challenges_data import CHALLENGES, CHALLENGE_LEVELS, LEVEL_UNLOCKS
from repositories.challenge_repository import get_completed_challenges, get_user_total_stars
from core.database import get_pool

import json
from urllib.parse import parse_qs

router = APIRouter()


# =========================================
# 📦 GET CHALLENGES
# =========================================
@router.post("/api/challenges")
async def get_challenges(request: Request):

    data = await request.json()
    init_data = data.get("initData")

    user_id = 0

    if init_data:
        try:
            parsed = parse_qs(init_data)
            if "user" in parsed:
                user_data = json.loads(parsed["user"][0])
                user_id = user_data.get("id", 0)
        except Exception as e:
            print("INIT DATA ERROR:", e)

    # ⭐ completed
    completed_rows = await get_completed_challenges(user_id)
    completed_map = {
        row["challenge_id"]: row["repeat_count"]
        for row in completed_rows
    }

    # ⭐ stars
    user_stars = await get_user_total_stars(user_id) or 0

    # 🔥 active habits
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT challenge_id, done_days, days
            FROM habits
            WHERE user_id=$1
            AND is_challenge=TRUE
            AND is_active=TRUE
        """, user_id)

    habit_map = {
        r["challenge_id"]: r for r in rows if r["challenge_id"]
    }

    modules = []

    for level_key, challenges in CHALLENGES.items():

        required = LEVEL_UNLOCKS.get(level_key, 0)
        is_unlocked = user_stars >= required

        module = {
            "level": level_key,
            "level_name": CHALLENGE_LEVELS["ru"][level_key],
            "required_stars": required,
            "is_unlocked": is_unlocked,
            "challenges": []
        }

        if not is_unlocked:
            modules.append(module)
            continue

        for ch in challenges:
            cid, title, texts, _ = ch

            repeat = completed_map.get(cid, 0)
            difficulty = min(repeat + 1, 3)

            base_days = {1: 7, 2: 10, 3: 13}

            active = habit_map.get(cid)

            if active:
                done = active["done_days"] or 0
                total = active["days"] or base_days[difficulty]
                is_active = True
            else:
                done = 0
                total = base_days[difficulty]
                is_active = False

            module["challenges"].append({
                "id": cid,
                "title": title,
                "description": texts,
                "difficulty": difficulty,
                "days": total,
                "current_section": {
                    "section": difficulty,
                    "days": total,
                    "stars": difficulty
                },
                "progress": {
                    "done_days": done,
                    "is_active": is_active
                }
            })

        modules.append(module)

    return {"modules": modules}


# =========================================
# 🚀 ACCEPT CHALLENGE
# =========================================
@router.post("/api/challenge/accept")
async def accept_challenge(request: Request):

    data = await request.json()
    init_data = data.get("initData")
    challenge_id = data.get("challenge_id")

    if not init_data or not challenge_id:
        return {"ok": False}

    user_id = 0

    try:
        parsed = parse_qs(init_data)
        if "user" in parsed:
            user_data = json.loads(parsed["user"][0])
            user_id = user_data.get("id", 0)
    except:
        return {"ok": False}

    pool = await get_pool()

    # ❌ уже активен
    async with pool.acquire() as conn:
        active = await conn.fetchrow("""
            SELECT 1 FROM habits
            WHERE user_id=$1
            AND challenge_id=$2
            AND is_active=TRUE
        """, user_id, challenge_id)

        if active:
            return {"ok": False, "error": "already_active"}

    completed_rows = await get_completed_challenges(user_id)
    completed_map = {
        r["challenge_id"]: r["repeat_count"]
        for r in completed_rows
    }

    for _, challenges in CHALLENGES.items():
        for ch in challenges:

            cid, title, texts, ctype = ch

            if cid != challenge_id:
                continue

            repeat = completed_map.get(cid, 0)
            difficulty = min(repeat + 1, 3)

            days_map = {1: 7, 2: 10, 3: 13}
            days = days_map[difficulty]

            description = texts.get(difficulty, "")

            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO habits
                    (user_id, name, description, days,
                     confirm_type, is_challenge,
                     challenge_id, difficulty, is_active)
                    VALUES ($1,$2,$3,$4,$5,TRUE,$6,$7,TRUE)
                """,
                    user_id, title, description,
                    days, ctype, cid, difficulty
                )

            return {
                "ok": True,
                "difficulty": difficulty,
                "days": days
            }

    return {"ok": False}