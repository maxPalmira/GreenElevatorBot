import os
from aiogram import executor, types
from src.loader import dp, db, bot
from src.handlers.user import dp as user_dp
from src.handlers.admin import dp as admin_dp
from src.filters import IsAdmin, IsUser
import logging
import asyncio

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@dp.message_handler()
async def debug_handler(message: types.Message):
    """Handler for unrecognized messages"""
    logger.info(f"🔍 Unhandled message from @{message.from_user.username} ({message.from_user.id}): {message.text}")
    await message.answer("Sorry, I don't understand that command. Try /start or /menu")

async def set_webhook(url):
    """Set webhook for the bot"""
    try:
        # Remove any existing webhook first
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Wait a bit to ensure webhook deletion is processed
        await asyncio.sleep(1)
        
        # Set the new webhook
        logger.info(f"🔗 Setting webhook to: {url}")
        await bot.set_webhook(url)
        
        # Check webhook status
        webhook_info = await bot.get_webhook_info()
        logger.info(f"ℹ️ Webhook status: {webhook_info}")
        
        if webhook_info.url == url:
            logger.info("✅ Webhook successfully set")
            return True
        else:
            logger.error(f"❌ Failed to set webhook: Expected URL {url}, got {webhook_info.url}")
            return False
    except Exception as e:
        logger.error(f"❌ Error setting webhook: {e}")
        return False

async def on_startup(dp):
    """Initialization function for webhook mode"""
    logger.info("🚀 Starting bot in webhook mode...")
    
    try:
        logger.info("💾 Initializing database...")
        db.create_tables()
        
        # Get Railway-provided URL
        webhook_host = os.getenv('RAILWAY_PUBLIC_DOMAIN')
        
        if webhook_host:
            webhook_url = f"https://{webhook_host}/webhook"
            logger.info(f"📡 Railway domain detected: {webhook_host}")
            
            # Set webhook
            success = await set_webhook(webhook_url)
            if not success:
                logger.error("⚠️ Failed to set webhook")
        else:
            logger.warning("⚠️ No Railway domain detected, webhook cannot be configured")
        
        me = await bot.get_me()
        logger.info(f"ℹ️ Bot Info: @{me.username} (ID: {me.id})")
        logger.info("✅ Bot started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise e

async def on_shutdown(dp):
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logger.info("Bye!")

def main():
    """Start the bot with webhook mode"""
    # Get port from environment or use default
    port = int(os.getenv('PORT', 8080))
    
    try:
        executor.start_webhook(
            dispatcher=dp,
            webhook_path='/webhook',
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host='0.0.0.0',
            port=port
        )
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        raise e

if __name__ == "__main__":
    main()
