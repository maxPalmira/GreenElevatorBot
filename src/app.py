import os
from aiogram import executor, types
from src.config import LOGS_DIR
from src.loader import dp, db, bot
from src.handlers.user import dp as user_dp
from src.handlers.admin import dp as admin_dp
from src.filters import IsAdmin, IsUser
import logging
import time
import asyncio
from aiogram.dispatcher.middlewares import BaseMiddleware
import logging.handlers
import json
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Define common logging format
log_format = '%(asctime)s %(levelname)s:%(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# Configure main file handler
file_handler = logging.handlers.RotatingFileHandler(
    os.path.join(LOGS_DIR, 'bot.log'),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter(log_format, date_format))

# Configure heartbeat file handler (smaller size, fewer backups)
heartbeat_handler = logging.handlers.RotatingFileHandler(
    os.path.join(LOGS_DIR, 'heartbeat.log'),
    maxBytes=1*1024*1024,  # 1MB
    backupCount=2,
    encoding='utf-8'
)
heartbeat_handler.setFormatter(logging.Formatter(log_format, date_format))

# Create heartbeat filter
class HeartbeatFilter(logging.Filter):
    def filter(self, record):
        return "Bot Status - Uptime:" not in record.getMessage()

# Create inverse heartbeat filter
class OnlyHeartbeatFilter(logging.Filter):
    def filter(self, record):
        return "Bot Status - Uptime:" in record.getMessage()

# Add filters to handlers
file_handler.addFilter(HeartbeatFilter())
heartbeat_handler.addFilter(OnlyHeartbeatFilter())

# Configure console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format, date_format))
console_handler.addFilter(HeartbeatFilter())  # Don't show heartbeats in console

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers = []  # Remove any existing handlers
root_logger.addHandler(file_handler)
root_logger.addHandler(heartbeat_handler)
root_logger.addHandler(console_handler)

# Get our logger and configure aiogram logger
logger = logging.getLogger(__name__)
aiogram_logger = logging.getLogger('aiogram')

def format_json(data):
    """Format JSON data for human readability with timestamp"""
    try:
        if isinstance(data, str):
            data = json.loads(data)
        
        # Add timestamp to the data if it's an update
        if isinstance(data, dict) and 'message' in data:
            msg_date = datetime.fromtimestamp(data['message']['date'])
            data['message']['date_human'] = msg_date.strftime(date_format)
            
        return json.dumps(data, indent=2, ensure_ascii=False)
    except:
        return str(data)

class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging bot updates and heartbeat"""
    def __init__(self):
        super().__init__()
        self.last_poll_time = time.time()
        self.heartbeat_task = None
        self.is_running = True
        self.start_time = time.time()
        self.message_count = 0
    
    async def heartbeat(self):
        """Send heartbeat messages every 5 seconds"""
        while self.is_running:
            try:
                current_time = time.time()
                uptime = current_time - self.start_time
                hours = int(uptime // 3600)
                minutes = int((uptime % 3600) // 60)
                seconds = int(uptime % 60)
                logger.info(f"💗 Bot Status - Uptime: {hours:02d}:{minutes:02d}:{seconds:02d} | Messages: {self.message_count}")
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat: {e}")
                await asyncio.sleep(5)  # Still wait before retry
    
    async def on_pre_process_update(self, update: types.Update, data: dict):
        """Log updates as they come in"""
        current_time = time.time()
        time_since_last = current_time - self.last_poll_time
        self.last_poll_time = current_time
        self.message_count += 1
        
        if update:
            pretty_update = format_json(update.to_python())
            logger.info(f"📥 Received update after {time_since_last:.1f}s:\n{pretty_update}")
        else:
            logger.debug(f"🔄 Polling cycle completed after {time_since_last:.1f}s (no updates)")
    
    def start_heartbeat(self):
        """Start the heartbeat task"""
        self.start_time = time.time()
        loop = asyncio.get_event_loop()
        self.heartbeat_task = loop.create_task(self.heartbeat())
    
    def stop_heartbeat(self):
        """Stop the heartbeat task"""
        self.is_running = False
        if self.heartbeat_task:
            self.heartbeat_task.cancel()

# Create and register middleware
logging_middleware = LoggingMiddleware()
dp.setup_middleware(logging_middleware)

# Register handlers
from src.handlers.user import dp as user_dp
from src.handlers.admin import dp as admin_dp

@dp.message_handler()
async def debug_handler(message: types.Message):
    """Handler for unrecognized messages"""
    logger.info(f"🔍 Unhandled message from @{message.from_user.username} ({message.from_user.id}): {message.text}")
    await message.answer("Sorry, I don't understand that command. Try /start or /menu")

async def on_startup(dp):
    """Initialization function executed when bot starts"""
    logger.info("🚀 Starting bot...")
    try:
        # Delete webhook before polling
        logger.info("🔄 Removing webhook...")
        await bot.delete_webhook(drop_pending_updates=True)
        webhook_info = await bot.get_webhook_info()
        logger.info(f"ℹ️ Webhook status: {webhook_info}")
        
        logger.info("💾 Initializing database...")
        db.create_tables()
        logger.info("✅ Bot started successfully!")
        
        me = await bot.get_me()
        logger.info(f"ℹ️ Bot Info: @{me.username} (ID: {me.id})")
        logger.info(f"ℹ️ Polling started - waiting for messages...")
        
        # Start heartbeat monitoring
        logging_middleware.start_heartbeat()
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise e

async def on_shutdown(dp):
    """Cleanup function executed when bot stops"""
    logger.info("🛑 Stopping bot...")
    try:
        # Stop heartbeat monitoring
        logging_middleware.stop_heartbeat()
        logger.info("✅ Bot stopped successfully!")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")
        raise e

def main():
    """Start the bot in polling mode"""
    logger.info("🔄 Starting bot in polling mode...")
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        timeout=30,  # Polling timeout
        relax=1.0    # Time between polling requests
    )

if __name__ == '__main__':
    main()
