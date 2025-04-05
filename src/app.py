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
    'errors': []
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
        # Check webhook status
        webhook_info = await bot.get_webhook_info()
        
        # Get Git version
        try:
            git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
        except:
            git_hash = None
            
        response = {
            "status": "ok" if initialization_status['initialized'] else "error",
            "version": git_hash,
            "timestamp": datetime.now().isoformat(),
            "uptime": str(datetime.now() - initialization_status['start_time']) if initialization_status['start_time'] else None,
            "webhook": {
                "url": webhook_info.url,
                "pending_updates": webhook_info.pending_update_count
            },
            "initialization": initialization_status
        }
        
        if not webhook_info.url:
            response["status"] = "error"
            response["message"] = "Webhook not set"
            return web.json_response(response, status=500)
            
        if not initialization_status['initialized']:
            response["status"] = "error"
            response["message"] = "Bot not fully initialized"
            return web.json_response(response, status=500)
            
        return web.json_response(response)
        
    except Exception as e:
        error_response = {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }
        logger.error(f"Health check failed: {str(e)}")
        return web.json_response(error_response, status=500)

async def logs_handler(request):
    """Endpoint to get recent application logs"""
    return web.json_response({
        "logs": [f"[{log['timestamp']}] {log['level']}: {log['message']}" 
                for log in application_logs]
    })

async def init_status_handler(request):
    """Endpoint to get initialization status"""
    return web.json_response(initialization_status)

async def on_startup(dp):
    """Startup handler with better status tracking"""
    log_with_storage(logging.INFO, "Starting initialization process...")
    try:
        initialization_status['start_time'] = datetime.now()
        log_with_storage(logging.INFO, "Checking environment variables...")
        
        # Check environment variables
        if not BOT_TOKEN:
            initialization_status['env_status'] = 'Missing BOT_TOKEN'
            log_with_storage(logging.ERROR, "BOT_TOKEN environment variable is not set!")
            raise ValueError("BOT_TOKEN environment variable is not set!")
        initialization_status['env_status'] = 'OK'
        log_with_storage(logging.INFO, "Environment variables OK")
        
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
            
        # Set webhook
        log_with_storage(logging.INFO, "Setting up webhook...")
        webhook_url = f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}/webhook"
        await bot.set_webhook(webhook_url)
        log_with_storage(logging.INFO, f"Webhook set to: {webhook_url}")
        
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
