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
from src.config import BOT_TOKEN
import json
import traceback

# Custom JSON Encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Keep track of initialization status
initialization_status = {
    'initialized': False,
    'env_status': 'Not checked',
    'db_status': 'Not checked',
    'start_time': None,
    'errors': [],
    'webhook_url': None  # Store webhook URL for fallback
}

# In-memory log storage
application_logs = []

def log_with_storage(level, message):
    """Log message and store it in memory"""
    logger.log(level, message)
    application_logs.append({
        'timestamp': datetime.now().isoformat(),
        'level': logging.getLevelName(level),
        'message': message
    })
    # Keep only last 100 logs
    if len(application_logs) > 100:
        application_logs.pop(0)

# Create health endpoints for Railway
async def health_handler(request):
    """Main health check endpoint"""
    try:
        # Basic response structure
        response = {
            "status": "initializing",
            "timestamp": datetime.now(),
            "checks": {
                "database": "not_checked",
                "webhook": "not_checked",
                "initialization": initialization_status
            },
            "errors": []
        }
        
        # Check database connection
        try:
            await db.test_connection()
            response["checks"]["database"] = "ok"
        except Exception as e:
            response["checks"]["database"] = "error"
            response["errors"].append(f"Database error: {str(e)}")
            
        # Check webhook status
        try:
            webhook_info = await bot.get_webhook_info()
            webhook_url = webhook_info.url or initialization_status.get('webhook_url', '')
            response["checks"]["webhook"] = "ok" if webhook_url else "error"
            response["webhook_info"] = {
                "url": webhook_url,
                "pending_updates": webhook_info.pending_update_count
            }
        except Exception as e:
            response["checks"]["webhook"] = "error"
            response["errors"].append(f"Webhook error: {str(e)}")
            
        # Overall status determination
        if response["errors"]:
            response["status"] = "error"
        elif not initialization_status['initialized']:
            response["status"] = "initializing"
        else:
            response["status"] = "ok"
            
        # Return with appropriate status code
        status_code = 200 if response["status"] == "ok" else 503
        return web.json_response(response, status=status_code, dumps=lambda obj: json.dumps(obj, cls=DateTimeEncoder))
        
    except Exception as e:
        error_response = {
            "status": "error",
            "timestamp": datetime.now(),
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return web.json_response(error_response, status=500, dumps=lambda obj: json.dumps(obj, cls=DateTimeEncoder))

async def logs_handler(request):
    """Endpoint to get recent application logs"""
    return web.json_response({
        "logs": [f"[{log['timestamp']}] {log['level']}: {log['message']}" 
                for log in application_logs]
    })

async def init_status_handler(request):
    """Endpoint to get initialization status"""
    # Create a copy with serializable datetime
    init_status = initialization_status.copy()
    if init_status['start_time']:
        init_status['start_time'] = init_status['start_time'].isoformat() if isinstance(init_status['start_time'], datetime) else init_status['start_time']
    return web.json_response(init_status)

async def on_startup(dp):
    """Startup handler with better status tracking"""
    log_with_storage(logging.INFO, "Starting initialization process...")
    try:
        initialization_status['start_time'] = datetime.now()
        
        # FIRST: Delete any existing webhook to ensure clean state
        await bot.delete_webhook()
        log_with_storage(logging.INFO, "Cleared existing webhook configuration")
        
        # Set webhook BEFORE any other operations
        log_with_storage(logging.INFO, "Setting up webhook...")
        webhook_url = f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}/webhook"
        await bot.set_webhook(webhook_url, drop_pending_updates=True)  # Drop any pending updates to prevent conflicts
        
        # Store webhook URL for fallback
        initialization_status['webhook_url'] = webhook_url
        
        # Verify webhook was set
        webhook_info = await bot.get_webhook_info()
        if not webhook_info.url:
            log_with_storage(logging.ERROR, "Failed to set webhook - URL is empty")
            raise RuntimeError("Failed to set webhook - URL is empty")
            
        log_with_storage(logging.INFO, f"Webhook set and verified at: {webhook_url}")
        
        # THEN: Check environment variables
        log_with_storage(logging.INFO, "Checking environment variables...")
        if not BOT_TOKEN:
            initialization_status['env_status'] = 'Missing BOT_TOKEN'
            log_with_storage(logging.ERROR, "BOT_TOKEN environment variable is not set!")
            raise ValueError("BOT_TOKEN environment variable is not set!")
        initialization_status['env_status'] = 'OK'
        
        # Initialize database
        log_with_storage(logging.INFO, "Initializing database...")
        try:
            db.connect()
            initialization_status['db_status'] = 'OK'
            log_with_storage(logging.INFO, "Database initialization successful")
        except Exception as e:
            initialization_status['db_status'] = f'Failed: {str(e)}'
            log_with_storage(logging.ERROR, f"Database initialization failed: {str(e)}")
            raise
            
        # Mark as initialized if everything is OK
        initialization_status['initialized'] = True
        log_with_storage(logging.INFO, "Bot successfully initialized")
        
    except Exception as e:
        error_msg = f"Startup failed: {str(e)}"
        initialization_status['errors'].append(error_msg)
        log_with_storage(logging.ERROR, error_msg)
        raise

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
    
    # Add health endpoints
    app.router.add_get('/health', health_handler)
    app.router.add_get('/health/logs', logs_handler)
    app.router.add_get('/health/init', init_status_handler)
    
    # Configure webhook settings
    webhook_path = '/webhook'
    
    try:
        # Start the web app with webhook handling
        executor.set_webhook(
            dispatcher=dp,
            webhook_path=webhook_path,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            web_app=app
        )
        
        web.run_app(
            app,
            host='0.0.0.0',
            port=port
        )
    except Exception as e:
        log_with_storage(logging.ERROR, f"❌ Webhook error: {e}")
        raise e

if __name__ == "__main__":
    main()
