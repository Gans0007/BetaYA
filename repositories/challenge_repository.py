from database import get_pool


# =====================================================
# 🔹 Репозиторий: получить общее количество ⭐ пользователя
#     - только SQL
#     - не содержит бизнес-логики
#     - не использует Telegram
# =====================================================
async def get_user_total_stars(user_id: int) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT total_stars FROM users WHERE user_id=$1",
            user_id
        )


# =====================================================
# 🔹 Репозиторий: получить активные челленджи пользователя
#     - только SQL
#     - возвращает challenge_id и сложность
# =====================================================
async def get_active_challenges(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT challenge_id, difficulty
            FROM habits
            WHERE user_id=$1 AND is_challenge=TRUE
        """, user_id)


# =====================================================
# 🔹 Репозиторий: получить завершённые челленджи пользователя
#     - только SQL
#     - возвращает challenge_id и repeat_count
# =====================================================
async def get_completed_challenges(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT challenge_id, repeat_count
            FROM completed_challenges
            WHERE user_id=$1
        """, user_id)


# =====================================================
# 🔹 Репозиторий: добавить челлендж в активные
#     - запись челленджа в habits
#     - никакой логики, только SQL
# =====================================================
async def insert_challenge_to_active(
    user_id: int,
    title: str,
    desc: str,
    days: int,
    ctype: str,
    cid: str,
    difficulty: int
):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO habits
                (user_id, name, description, days, confirm_type,
                 is_challenge, challenge_id, difficulty)
            VALUES ($1,$2,$3,$4,$5,TRUE,$6,$7)
        """, user_id, title, desc, days, ctype, cid, difficulty)


# =====================================================
# 🔹 Репозиторий: отметить челлендж завершённым
#     - добавляет запись в completed_challenges
#     - чистый SQL-слой
# =====================================================
async def mark_challenge_completed(
    user_id: int,
    title: str,
    level_key: str,
    cid: str,
    new_repeat: int
):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO completed_challenges
                (user_id, challenge_name, level_key, challenge_id, repeat_count)
            VALUES ($1,$2,$3,$4,$5)
        """, user_id, title, level_key, cid, new_repeat)
