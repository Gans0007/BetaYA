import asyncio
from databases import Database

DATABASE_URL = "postgresql://postgres:FQLO2o3Hztd15dreWkml@yourambition.pgwc9a5k3t4j6h15kvjqjse7t0.postgres.ubicloud.com:5432/postgres"
database = Database(DATABASE_URL)

async def init_postgres_db():
    await database.connect()

    await database.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        name TEXT,
        xp_balance INTEGER DEFAULT 0,
        usdt_balance REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_habits INTEGER DEFAULT 0,
        special_reward INTEGER DEFAULT 0,
        finished_habits INTEGER DEFAULT 0,
        finished_challenges INTEGER DEFAULT 0,
        active_days INTEGER DEFAULT 0,
        current_streak INTEGER DEFAULT 0,
        best_streak INTEGER DEFAULT 0,
        last_confirmation_date DATE,
        active_referrals INTEGER DEFAULT 0
    );
    """)

    await database.execute("""
    CREATE TABLE IF NOT EXISTS referrals (
        referrer_id BIGINT,
        invited_id BIGINT PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (referrer_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (invited_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)

    await database.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        name TEXT NOT NULL,
        days INTEGER NOT NULL,
        description TEXT,
        done_days INTEGER DEFAULT 0,
        is_challenge BOOLEAN DEFAULT FALSE,
        confirm_type TEXT DEFAULT 'media',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)

    await database.execute("""
    CREATE TABLE IF NOT EXISTS pending_videos (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        video_link TEXT NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        approved BOOLEAN DEFAULT FALSE,
        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)

    await database.execute("""
    CREATE TABLE IF NOT EXISTS reward_history (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        amount REAL NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('xp', 'usdt')),
        reason TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)

    await database.execute("""
    CREATE TABLE IF NOT EXISTS confirmations (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        habit_id INTEGER NOT NULL,
        datetime TIMESTAMP,
        file_id TEXT,
        file_type TEXT,
        confirmed BOOLEAN,
        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
    );
    """)

    await database.execute("""
    CREATE TABLE IF NOT EXISTS timezones (
        user_id BIGINT PRIMARY KEY,
        offset_minutes INTEGER
    );
    """)

    await database.execute("""
    CREATE TABLE IF NOT EXISTS reset_flags (
        user_id BIGINT,
        date DATE,
        PRIMARY KEY (user_id, date),
        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)

    await database.disconnect()
    print("✅ PostgreSQL таблицы инициализированы.")

if __name__ == "__main__":
    asyncio.run(init_postgres_db())
