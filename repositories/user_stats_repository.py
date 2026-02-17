# repositories/user_stats_repository.py

from datetime import date, timedelta


# +1 завершённая привычка
async def increment_finished_habits(conn, user_id: int):
    return await conn.execute("""
        INSERT INTO user_stats (user_id, finished_habits)
        VALUES ($1, 1)
        ON CONFLICT (user_id) DO UPDATE
        SET finished_habits = user_stats.finished_habits + 1
    """, user_id)


# +1 завершённый челлендж
async def increment_finished_challenges(conn, user_id: int):
    return await conn.execute("""
        INSERT INTO user_stats (user_id, finished_challenges)
        VALUES ($1, 1)
        ON CONFLICT (user_id) DO UPDATE
        SET finished_challenges = user_stats.finished_challenges + 1
    """, user_id)


# +N звёзд
async def increment_total_stars(conn, user_id: int, stars: int):
    return await conn.execute("""
        INSERT INTO user_stats (user_id, total_stars)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO UPDATE
        SET total_stars = user_stats.total_stars + $2
    """, user_id, stars)

# +XP
async def increment_xp(conn, user_id: int, xp: float):
    return await conn.execute("""
        INSERT INTO user_stats (user_id, xp)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO UPDATE
        SET xp = user_stats.xp + $2
    """, user_id, xp)

# +всего дней
async def set_total_confirmed_days(conn, user_id: int, total_days: int):
    return await conn.execute("""
        INSERT INTO user_stats (user_id, total_confirmed_days)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO UPDATE
        SET total_confirmed_days = EXCLUDED.total_confirmed_days
    """, user_id, total_days)

#стрик
async def update_user_streak(conn, user_id: int):
    user = await conn.fetchrow("""
        SELECT current_streak, max_streak, last_streak_date
        FROM user_stats
        WHERE user_id = $1
    """, user_id)

    today = date.today()

    if not user:
        await conn.execute("""
            INSERT INTO user_stats (user_id, current_streak, max_streak, last_streak_date)
            VALUES ($1, 1, 1, $2)
        """, user_id, today)
        return 1

    last_date = user["last_streak_date"]

    if last_date is None:
        await conn.execute("""
            UPDATE user_stats
            SET current_streak = 1,
                max_streak = 1,
                last_streak_date = $1
            WHERE user_id = $2
        """, today, user_id)
        return 1

    if last_date == today - timedelta(days=1):
        new_current = user["current_streak"] + 1
        new_max = max(new_current, user["max_streak"])

        await conn.execute("""
            UPDATE user_stats
            SET current_streak = $1,
                max_streak = $2,
                last_streak_date = $3
            WHERE user_id = $4
        """, new_current, new_max, today, user_id)

        return new_current

    if last_date == today:
        return user["current_streak"]

    await conn.execute("""
        UPDATE user_stats
        SET current_streak = 1,
            last_streak_date = $1
        WHERE user_id = $2
    """, today, user_id)

    return 1


