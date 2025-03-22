from dotenv import load_dotenv
import os

# Load .env only once when config is imported
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Optional: raise errors if key variables are missing
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")
