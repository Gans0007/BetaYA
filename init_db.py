import aiosqlite
import asyncio
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "habits.db"

async def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("PRAGMA foreign_keys = ON;")

        # Таблица пользователей
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id                INTEGER PRIMARY KEY,
            name                   TEXT,
            xp_balance             INTEGER DEFAULT 0,
            usdt_balance           REAL DEFAULT 0,
            created_at             TEXT,
            created_habits         INTEGER DEFAULT 0,
            special_reward         INTEGER DEFAULT 0,
            finished_habits        INTEGER DEFAULT 0,
            finished_challenges    INTEGER DEFAULT 0,
            active_days            INTEGER DEFAULT 0,
            current_streak         INTEGER DEFAULT 0,
            best_streak            INTEGER DEFAULT 0,
            last_confirmation_date TEXT,
            active_referrals       INTEGER DEFAULT 0
        );
        """)

        # Рефералы
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                referrer_id INTEGER,
                invited_id INTEGER PRIMARY KEY,
                created_at TEXT,
                is_active INTEGER DEFAULT 0,
                FOREIGN KEY (referrer_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (invited_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
        """)



        # Добавление колонок, если не хватает
        for col_name, col_type in [
            ("active_days", "INTEGER DEFAULT 0"),
            ("current_streak", "INTEGER DEFAULT 0"),
            ("best_streak", "INTEGER DEFAULT 0"),
            ("last_confirmation_date", "TEXT")
        ]:
            try:
                await conn.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};")
            except aiosqlite.OperationalError:
                pass  # колонка уже существует

        # Таблица привычек
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL,
            name             TEXT    NOT NULL,
            days             INTEGER NOT NULL,
            description      TEXT,
            done_days        INTEGER DEFAULT 0,
            is_challenge     INTEGER DEFAULT 0,
            confirm_type     TEXT    DEFAULT 'media',
            created_at       TEXT,
            is_active        INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """)


        # Таблица загруженных видео на проверку
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS pending_videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            video_link TEXT NOT NULL,
            submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            approved INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """)

        # Таблица истории наград
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS reward_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('xp', 'usdt')),
            reason TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """)


        # Таблица подтверждений
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS confirmations (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            habit_id     INTEGER NOT NULL,
            datetime     TEXT,
            file_id      TEXT,
            file_type    TEXT,
            confirmed    INTEGER,
            FOREIGN KEY(user_id)  REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY(habit_id) REFERENCES habits(id)    ON DELETE CASCADE
        );
        """)

        # Таблица часовых поясов
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS timezones (
            user_id        INTEGER PRIMARY KEY,
            offset_minutes INTEGER
        );
        """)

        # Таблица флагов сброса
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS reset_flags (
            user_id INTEGER,
            date    TEXT,
            PRIMARY KEY (user_id, date),
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """)

        await conn.commit()

    print("✅ База данных инициализирована (асинхронно).")

# Если нужно запустить вручную:
# asyncio.run(init_db())
