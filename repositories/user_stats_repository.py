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

