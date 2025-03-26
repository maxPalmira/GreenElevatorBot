import os
from aiogram import executor, types
from src.loader import dp, db, bot
from src.handlers.user import dp as user_dp
from src.handlers.admin import dp as admin_dp
from src.filters import IsAdmin, IsUser
import logging
import asyncio
from datetime import datetime
import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

# Initialize FastAPI app
app = FastAPI()

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment."""
    try:
        # Try to get bot info as part of health check
        me = await bot.get_me()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "message": "Bot is running",
                "bot_info": f"@{me.username} (ID: {me.id})",
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

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

async def on_startup(app):
    """Initialization function for FastAPI startup"""
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

async def on_shutdown(app):
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logger.info("Bye!")

# Register startup and shutdown events
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)

# Add webhook route to FastAPI app
@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle webhook requests from Telegram"""
    try:
        update_data = await request.json()
        await dp.process_update(types.Update(**update_data))
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return Response(status_code=500)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
