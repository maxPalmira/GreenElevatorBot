import os
from aiogram import executor, types
from src.loader import dp, db, bot
from src.handlers.user import dp as user_dp
from src.handlers.admin import dp as admin_dp
from src.filters import IsAdmin, IsUser
import logging
import asyncio
from aiohttp import web
import subprocess
from datetime import datetime

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create a health endpoint for Railway
async def health_handler(request):
    """Health check endpoint for Railway"""
    try:
        # Check webhook status
        webhook_info = await bot.get_webhook_info()
        
        # Get Git version
        try:
            git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
        except:
            git_hash = None
            
        response = {
            "status": "ok",
            "version": git_hash,
            "timestamp": datetime.now().isoformat(),
            "webhook": {
                "url": webhook_info.url,
                "pending_updates": webhook_info.pending_update_count
            }
        }
        
        if not webhook_info.url:
            response["status"] = "error"
            response["message"] = "Webhook not set"
            return web.json_response(response, status=500)
            
        return web.json_response(response)
        
    except Exception as e:
        return web.json_response({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, status=500)

@dp.message_handler()
async def debug_handler(message: types.Message):
    """Handler for unrecognized messages"""
    logger.info(f"🔍 Unhandled message from @{message.from_user.username} ({message.from_user.id}): {message.text}")
    await message.answer("Sorry, I don't understand that command. Try /start or /menu")

async def set_webhook(url, max_retries=3, initial_delay=1):
    """Set webhook for the bot with retries
    
    Args:
        url: Webhook URL to set
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries (will be exponentially increased)
    
    Returns:
        bool: True if webhook was set successfully, False otherwise
    
    Raises:
        RuntimeError: If webhook could not be set after all retries
    """
    for attempt in range(max_retries):
        try:
            # Remove any existing webhook first
            await bot.delete_webhook(drop_pending_updates=True)
            
            # Wait to ensure webhook deletion is processed
            await asyncio.sleep(initial_delay * (2 ** attempt))
            
            # Set the new webhook
            logger.info(f"🔗 Setting webhook to: {url} (attempt {attempt + 1}/{max_retries})")
            await bot.set_webhook(url)
            
            # Verify webhook was set
            webhook_info = await bot.get_webhook_info()
            logger.info(f"ℹ️ Webhook status: {webhook_info}")
            
            if webhook_info.url == url:
                logger.info("✅ Webhook successfully set")
                return True
            else:
                logger.error(f"❌ Webhook verification failed: Expected URL {url}, got {webhook_info.url}")
                
        except Exception as e:
            logger.error(f"❌ Error setting webhook (attempt {attempt + 1}/{max_retries}): {e}")
            
        if attempt < max_retries - 1:
            logger.info(f"🔄 Retrying webhook setup in {initial_delay * (2 ** attempt)} seconds...")
        
    raise RuntimeError(f"Failed to set webhook after {max_retries} attempts")

async def on_startup(dp):
    """Initialization function for webhook mode"""
    logger.info("🚀 Starting bot in webhook mode...")
    
    try:
        logger.info("💾 Initializing database...")
        # Connect to database (which automatically initializes tables)
        db.connect()
        
        # Get Railway-provided URL
        webhook_host = os.getenv('RAILWAY_PUBLIC_DOMAIN')
        
        if not webhook_host:
            raise RuntimeError("⚠️ No Railway domain detected, webhook cannot be configured")
            
        webhook_url = f"https://{webhook_host}/webhook"
        logger.info(f"📡 Railway domain detected: {webhook_host}")
        
        # Set webhook with retries
        try:
            await set_webhook(webhook_url)
        except RuntimeError as e:
            logger.error(f"❌ Critical error: {e}")
            # Exit the application if webhook setup fails
            raise SystemExit(1)
        
        me = await bot.get_me()
        logger.info(f"ℹ️ Bot Info: @{me.username} (ID: {me.id})")
        logger.info("✅ Bot started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise SystemExit(1)

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
    
    # Setup the web app
    app = web.Application()
    
    # Add health endpoint
    app.router.add_get('/health', health_handler)
    
    # Configure webhook settings
    webhook_path = '/webhook'
    
    # Setup webhook handling
    executor.set_webhook(
        dispatcher=dp,
        webhook_path=webhook_path,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        web_app=app
    )
    
    try:
        # Start the web app
        web.run_app(
            app,
            host='0.0.0.0',
            port=port
        )
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        raise e

if __name__ == "__main__":
    main()
