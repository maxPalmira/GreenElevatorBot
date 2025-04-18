# Add comment at the top tracking our changes
# Changes:
# - 2025-08-30: Removed SQLite code and standardized on PostgreSQL
# - 2025-04-14: Removed polling flag and fixed database initialization
# - 2025-04-09: Modified bot initialization to ensure webhook-only mode

import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from src.config import BOT_TOKEN, ADMINS, DATABASE_URL
import logging
import asyncio
import sys
from src.database import Database

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

# Initialize bot with webhook mode
bot = RetryBot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Initialize PostgreSQL database 
from src.utils.db.pg_database import PostgresDatabase
logging.info("Initializing PostgreSQL database")
db = PostgresDatabase(DATABASE_URL)
from src.utils.db.pg_database import create_db as init_db

# Log initialization
token_preview = BOT_TOKEN[:5] + "..." if BOT_TOKEN else "Not Set"
logging.info(f"Bot initialized with token: {token_preview}")
logging.info(f"Admin IDs: {ADMINS}")
logging.info(f"Using database: PostgreSQL")