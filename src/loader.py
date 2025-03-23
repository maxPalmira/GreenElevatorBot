from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from src.config import BOT_TOKEN, ADMINS, DATABASE_PATH
from src.utils.db.database import Database
from src.utils.db.init_db import init_db
import logging
import asyncio
import sys

# Configure retry settings
RETRY_DELAYS = [1, 3, 5, 10]
MAX_RETRIES = 5

# Check if bot token is available
if not BOT_TOKEN:
    logging.error("No bot token provided. Please set BOT_TOKEN in .env file")
    sys.exit(1)

class RetryBot(Bot):
    async def request(self, method, data=None, *args, **kwargs):
        """Override request method to add retry logic"""
        last_exc = Exception("Maximum retries exceeded")
        for delay in RETRY_DELAYS:
            try:
                return await super().request(method, data, *args, **kwargs)
            except Exception as e:
                last_exc = e
                logging.warning(f"Request failed, retrying in {delay} seconds...")
                await asyncio.sleep(delay)
        raise last_exc

# Initialize bot with retry logic
bot = RetryBot(
    token=BOT_TOKEN,  # We've verified it's not None above
    parse_mode=types.ParseMode.HTML,
)

# Storage for FSM
storage = MemoryStorage()

# Initialize dispatcher
dp = Dispatcher(bot, storage=storage)

# Initialize database
db = Database(DATABASE_PATH)
init_db()  # Initialize database with default data

# Log initialization
token_preview = BOT_TOKEN[:5] + "..." if BOT_TOKEN else "Not Set"
logging.info(f"Bot initialized with token: {token_preview}")
logging.info(f"Admin IDs: {ADMINS}")