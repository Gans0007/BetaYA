from datetime import datetime, timezone


# ================================
#  Репозиторий: только SQL
# ================================

async def get_user_timezone(conn, user_id: int):
    return await conn.fetchrow(
        "SELECT timezone FROM users WHERE user_id=$1",
        user_id
    )


async def get_habit_for_start(conn, habit_id: int):
    return await conn.fetchrow("""
        SELECT name, is_challenge
        FROM habits
        WHERE id=$1
    """, habit_id)


async def get_last_confirmation_for_habit(conn, user_id: int, habit_id: int):
    return await conn.fetchrow("""
        SELECT datetime FROM confirmations
        WHERE user_id=$1 AND habit_id=$2
        ORDER BY datetime DESC LIMIT 1
    """, user_id, habit_id)


async def habit_exists(conn, habit_id: int) -> bool:
    count = await conn.fetchval(
        "SELECT COUNT(*) FROM habits WHERE id=$1",
        habit_id
    )
    return count > 0


async def update_last_confirmation_media(
    conn,
    file_id: str,
    file_type: str,
    user_id: int,
    habit_id: int
):
    return await conn.execute("""
        UPDATE confirmations
        SET file_id=$1, file_type=$2, datetime=NOW(), confirmed=TRUE
        WHERE id = (
            SELECT id FROM confirmations
            WHERE user_id=$3 AND habit_id=$4
            ORDER BY datetime DESC
            LIMIT 1
        )
    """, file_id, file_type, user_id, habit_id)


async def insert_confirmation(
    conn,
    user_id: int,
    habit_id: int,
    file_id: str,
    file_type: str
):
    return await conn.execute("""
        INSERT INTO confirmations (user_id, habit_id, datetime, file_id, file_type, confirmed)
        VALUES ($1, $2, NOW(), $3, $4, TRUE)
    """, user_id, habit_id, file_id, file_type)


async def increment_done_days(conn, habit_id: int):
    return await conn.execute(
        "UPDATE habits SET done_days = done_days + 1 WHERE id=$1",
        habit_id
    )


async def get_confirmations_count_today(conn, user_id: int) -> int:
    return await conn.fetchval("""
        SELECT COUNT(DISTINCT habit_id)
        FROM confirmations
        WHERE user_id = $1
          AND DATE(datetime AT TIME ZONE 'Europe/Kyiv') = CURRENT_DATE
    """, user_id)


async def get_user_notification_data(conn, user_id: int):
    return await conn.fetchrow("""
        SELECT 
            has_access, 
            access_until, 
            total_confirmed_days, 
            share_confirmation_media, 
            nickname,
            notification_tone
        FROM users 
        WHERE user_id=$1
    """, user_id)



def choose_target_chat(user_row) -> int:
    has_access = user_row["has_access"]
    access_until = user_row["access_until"]

    sub_active = bool(
        has_access and
        access_until and
        access_until > datetime.now(timezone.utc)
    )

    # те же самые chat_id, что и в исходнике
    return -1002392347850 if sub_active else -1002375148535


async def get_habit_progress(conn, habit_id: int):
    return await conn.fetchrow("""
        SELECT name, days, done_days 
        FROM habits WHERE id=$1
    """, habit_id)


async def get_challenge_habit(conn, habit_id: int):
    return await conn.fetchrow("""
        SELECT user_id, name, days, done_days, is_challenge, challenge_id
        FROM habits WHERE id=$1
    """, habit_id)


async def get_completed_challenge(conn, user_id: int, challenge_id: int):
    return await conn.fetchrow("""
        SELECT repeat_count FROM completed_challenges
        WHERE user_id=$1 AND challenge_id=$2
    """, user_id, challenge_id)


async def update_completed_challenge(
    conn,
    new_count: int,
    user_id: int,
    challenge_id: int
):
    return await conn.execute("""
        UPDATE completed_challenges
        SET repeat_count=$1, completed_at=NOW()
        WHERE user_id=$2 AND challenge_id=$3
    """, new_count, user_id, challenge_id)


async def insert_completed_challenge(
    conn,
    user_id: int,
    challenge_name: str,
    challenge_id: int
):
    return await conn.execute("""
        INSERT INTO completed_challenges (user_id, challenge_name, level_key, challenge_id, repeat_count)
        VALUES ($1, $2, 'auto', $3, 1)
    """, user_id, challenge_name, challenge_id)


async def update_user_challenge_counters(
    conn,
    stars_delta: int,
    user_id: int
):
    return await conn.execute("""
        UPDATE users 
        SET finished_challenges = finished_challenges + 1,
            total_stars = total_stars + $1
        WHERE user_id=$2
    """, stars_delta, user_id)
