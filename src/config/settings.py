import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in .env file")

# LLM
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.1:8b")

# Database
POSTGRES_CONFIG = {
    'host': os.getenv("POSTGRES_HOST", "localhost"),
    'port': int(os.getenv("POSTGRES_PORT", 5432)),
    'database': os.getenv("POSTGRES_NAME", "ai_bot_db"),
    'user': os.getenv("POSTGRES_USER", "ai_bot_user"),
    'password': os.getenv("POSTGRES_PASSWD")
}

# Voice settings
VOICE_ENABLED = os.getenv("VOICE_ENABLED", "True").lower() == "true"
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", 10))