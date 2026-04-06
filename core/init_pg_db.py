from core.database import get_pool

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
                notification_tone TEXT DEFAULT 'friend',
                share_confirmation_media BOOLEAN DEFAULT TRUE,
                timezone TEXT DEFAULT 'Europe/Kyiv',
                joined_at TIMESTAMPTZ DEFAULT NOW(),
                referral_code TEXT,
                paid_out DOUBLE PRECISION DEFAULT 0,    
                has_access BOOLEAN DEFAULT FALSE,
                access_until TIMESTAMPTZ,
                last_global_rank INTEGER,
                last_rank_update DATE,
                subscription_notified BOOLEAN DEFAULT FALSE
            )
        """)

        # -------------------------------
        # 🔹 Таблица статистики пользователей
        # -------------------------------
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                finished_habits INTEGER DEFAULT 0,
                finished_challenges INTEGER DEFAULT 0,
                total_stars INTEGER DEFAULT 0,
                xp DOUBLE PRECISION DEFAULT 0,
                total_confirmed_days INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                max_streak INTEGER DEFAULT 0,
                last_streak_date DATE,
                league TEXT DEFAULT 'Бронза I',
                league_emoji TEXT DEFAULT '🥉',
                usdt_payments NUMERIC(18,6) DEFAULT 0
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
        # 🔹 Таблица достижений пользователя (user_achievements)
        # -------------------------------
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_id BIGINT NOT NULL,
                achievement_code TEXT NOT NULL,
                earned_at TIMESTAMPTZ DEFAULT NOW(),

                PRIMARY KEY (user_id, achievement_code),

                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
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
        # 🔹 Таблица событий пользователя (user_events)
        # -------------------------------
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_events (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                type TEXT NOT NULL, -- league_up / achievement / challenge_complete
                entity_id TEXT,
                value TEXT, 
                meta JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                is_seen BOOLEAN DEFAULT FALSE,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # -------------------------------
        # 🔹 Таблица задач на день (daily_tasks)
        # -------------------------------
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_tasks (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                text TEXT NOT NULL,
                planned_for_date DATE NOT NULL,

                status TEXT DEFAULT 'pending',
                position INT DEFAULT 0,
                is_deleted BOOLEAN DEFAULT FALSE,

                created_at TIMESTAMPTZ DEFAULT NOW(),

                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,

                UNIQUE(user_id, planned_for_date, text)
            )
        """)

        # -------------------------------
        # 🔹 Таблица напоминаний о планировании
        # -------------------------------
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS plan_reminders (
                user_id BIGINT PRIMARY KEY,
                remind_at TIME DEFAULT '20:00',

                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # -------------------------------
        # 🔹 Индексы для daily_tasks
        # -------------------------------
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_daily_tasks_user_date
            ON daily_tasks(user_id, planned_for_date)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_daily_tasks_user_status
            ON daily_tasks(user_id, status)
        """)

        # -------------------------------
        # 🔹 Индексы для событий
        # -------------------------------
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_events_user_id 
            ON user_events(user_id)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_events_user_seen 
            ON user_events(user_id, is_seen)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_events_type 
            ON user_events(type)
        """)

        # -------------------------------
        # 🔹 Индексы для ускорения запросов
        # -------------------------------
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_habits_user_id ON habits(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_completed_user_id ON completed_challenges(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_habits_challenge_id ON habits(challenge_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_completed_challenge_id ON completed_challenges(challenge_id)")

        # 🔥 Индексы для профиля

        await conn.execute("CREATE INDEX IF NOT EXISTS idx_confirmations_user_datetime ON confirmations(user_id, datetime)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_confirmations_user_datetime_habit ON confirmations(user_id, datetime, habit_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_habits_user_active ON habits(user_id, is_active)")

        print("✅ Таблицы успешно созданы или уже существуют.")
