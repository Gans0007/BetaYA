# repositories/user_stats_repository.py

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

