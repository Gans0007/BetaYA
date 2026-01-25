from database import get_pool

async def create_users_table():
    pool = await get_pool()
    async with pool.acquire() as conn:
        # -------------------------------
        # 🔹 Таблица пользователей
        # -------------------------------
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                nickname TEXT,
                username TEXT,
                first_name TEXT,
                finished_habits INTEGER DEFAULT 0,
                finished_challenges INTEGER DEFAULT 0,
                total_stars INTEGER DEFAULT 0,
                total_confirmed_days INTEGER DEFAULT 0,
                notification_tone TEXT DEFAULT 'friend',
                xp DOUBLE PRECISION DEFAULT 0,
                league TEXT DEFAULT 'Безответственный',
                league_emoji TEXT DEFAULT '🕳️',
                share_confirmation_media BOOLEAN DEFAULT TRUE,
                timezone TEXT DEFAULT 'Europe/Kyiv',
                joined_at TIMESTAMP DEFAULT NOW(),
                referral_code TEXT,
                payments DOUBLE PRECISION DEFAULT 0,
                paid_out DOUBLE PRECISION DEFAULT 0,    
                has_access BOOLEAN DEFAULT TRUE,
                access_until TIMESTAMPTZ,
                last_global_rank INTEGER,
                last_rank_update DATE,
                subscription_notified BOOLEAN DEFAULT FALSE
            )
        """)

        # -------------------------------
        # 🔹 Таблица привычек (habits)
        # -------------------------------
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name TEXT NOT NULL,
                days INTEGER NOT NULL,
                description TEXT,
                done_days INTEGER DEFAULT 0,
                is_challenge BOOLEAN DEFAULT FALSE,
                confirm_type TEXT DEFAULT 'media',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                is_active BOOLEAN DEFAULT TRUE,
                challenge_id TEXT,
                difficulty INTEGER DEFAULT 1,
                reset_streak INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # -------------------------------
        # 🔹 Таблица подтверждений (confirmations)
        # -------------------------------
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS confirmations (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                habit_id INTEGER NOT NULL,
                datetime TIMESTAMPTZ DEFAULT NOW(),
                file_id TEXT,
                file_type TEXT,
                confirmed BOOLEAN,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
            )
        """)

        # -------------------------------
        # 🔹 Таблица завершённых челленджей (completed_challenges)
        # -------------------------------
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS completed_challenges (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                challenge_name TEXT NOT NULL,
                level_key TEXT NOT NULL,
                challenge_id TEXT,
                repeat_count INTEGER DEFAULT 1,
                completed_at TIMESTAMPTZ DEFAULT NOW(),
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE(user_id, challenge_id)
            )
        """)

        # -------------------------------
        # 🔹 ТАБЛИЦА РЕФЕРАЛКИ (referrals)
        # -------------------------------
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id SERIAL PRIMARY KEY,
                affiliate_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                registered_at TIMESTAMPTZ DEFAULT NOW(),
                is_active BOOLEAN DEFAULT FALSE,
                active_at TIMESTAMPTZ,

                UNIQUE(affiliate_id, user_id),

                FOREIGN KEY(affiliate_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # -------------------------------
        # 🔹 Индексы для ускорения запросов
        # -------------------------------
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_habits_user_id ON habits(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_completed_user_id ON completed_challenges(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_habits_challenge_id ON habits(challenge_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_completed_challenge_id ON completed_challenges(challenge_id)")

        print("✅ Таблицы успешно созданы или уже существуют.")
