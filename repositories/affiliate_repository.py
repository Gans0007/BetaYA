# repositories/affiliate_repository.py

from database import get_pool


# ------------------------------------------
# Найти аффилиата по реферальному коду
# ------------------------------------------
async def get_affiliate_by_code(referral_code: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT user_id
            FROM users
            WHERE referral_code = $1
        """, referral_code)

    return row["user_id"] if row else None


# ------------------------------------------
# Проверить — есть ли у пользователя реферал
# ------------------------------------------
async def user_already_has_affiliate(user_id: int) -> bool:
    """
    Возвращает True, если user_id уже записан как чей-то реферал.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        exists = await conn.fetchval("""
            SELECT 1
            FROM referrals
            WHERE user_id = $1
        """, user_id)

    return bool(exists)


# ------------------------------------------
# Создать запись реферала
# ------------------------------------------
async def create_referral(affiliate_id: int, user_id: int) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO referrals (affiliate_id, user_id)
            VALUES ($1, $2)
        """, affiliate_id, user_id)


# ------------------------------------------
# Получить аффилиата по user_id (кто пригласил)
# ------------------------------------------
async def get_affiliate_for_user(user_id: int):
    """
    Возвращает affiliate_id или None.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("""
            SELECT affiliate_id
            FROM referrals
            WHERE user_id = $1
        """, user_id)


# ------------------------------------------
# Отметить реферала активным
# ------------------------------------------
async def mark_referral_active(user_id: int) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE referrals
            SET is_active = TRUE,
                active_at = NOW()
            WHERE user_id = $1
        """, user_id)

# ------------------------------------------
# Функция начисления денег партнёру
# ------------------------------------------
async def add_payment_to_affiliate(affiliate_id: int, amount: float):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET payments = payments + $1
            WHERE user_id = $2
        """, amount, affiliate_id)

# ------------------------------------------
# Функция получения баланса
# ------------------------------------------
async def get_payments(user_id: int) -> float:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("""
            SELECT payments
            FROM users
            WHERE user_id = $1
        """, user_id) or 0


# ------------------------------------------
# Статистика по партнёру
# ------------------------------------------
async def get_affiliate_stats(affiliate_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT
                COUNT(*) AS invited,
                COUNT(*) FILTER (WHERE is_active = TRUE) AS active
            FROM referrals
            WHERE affiliate_id = $1
        """, affiliate_id)

    return {
        "invited": row["invited"] or 0,
        "active": row["active"] or 0
    }


async def get_referral_code(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("""
            SELECT referral_code
            FROM users
            WHERE user_id = $1
        """, user_id)


# ------------------------------------------
# Если есть в юзерс, тогда не присваивать рефералку
# ------------------------------------------
async def user_exists_in_users_table(user_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        exists = await conn.fetchval("""
            SELECT 1
            FROM users
            WHERE user_id = $1
        """, user_id)

    return bool(exists)

# ------------------------------------------
# ДАТЬ СПИСОК РЕФЕРАЛОВ КНОПКА
# ------------------------------------------
async def get_referrals_list(affiliate_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT r.user_id, r.registered_at, r.is_active, r.active_at,
                   u.username
            FROM referrals r
            LEFT JOIN users u ON u.user_id = r.user_id
            WHERE r.affiliate_id = $1
            ORDER BY r.registered_at
        """, affiliate_id)


# ------------------------------------------
# ДАТЬ СПИСОК ВЫПЛАТ КНОПКА
# ------------------------------------------
async def get_payments_list(affiliate_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT r.user_id, r.active_at, u.username
            FROM referrals r
            LEFT JOIN users u ON u.user_id = r.user_id
            WHERE r.affiliate_id = $1 AND r.is_active = TRUE
            ORDER BY r.active_at
        """, affiliate_id)


