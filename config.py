import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")

CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
CHAT_USERNAME = os.getenv("CHAT_USERNAME")

PUBLIC_CHAT_ID = int(os.getenv("PUBLIC_CHAT_ID"))
PUBLIC_CHANNEL_ID = int(os.getenv("PUBLIC_CHANNEL_ID"))

DATABASE_URL = os.getenv("DATABASE_URL")
