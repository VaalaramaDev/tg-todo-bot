import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TIMEZONE = os.getenv("TIMEZONE", "UTC")
DB_PATH = os.getenv("DB_PATH", "data/todo.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
