import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env")

CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # пример: @yourchannel
CHAT_USERNAME = os.getenv("CHAT_USERNAME")        # пример: @yourchat

public_chat_id = os.getenv("PUBLIC_CHAT_ID")
if not public_chat_id:
    raise ValueError("❌ PUBLIC_CHAT_ID не найден в .env")
PUBLIC_CHAT_ID = int(public_chat_id)
ADMIN_ID = 900410719  # Замени на свой Telegram user ID

DB_PATH = Path(__file__).resolve().parent / "data" / "habits.db"
