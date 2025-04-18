"""
Application server for Telegram bot.
Created: 2024-03-09
Changes:
- Added async state update method
- Fixed app state management
"""

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
from time import perf_counter
from aiohttp.web_response import json_response

# Global app instance
app = None

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

# Modify the health handler to be more comprehensive
async def health_handler(request):
    """Health check endpoint that checks database and webhook status"""
    try:
        # During startup, return 200 OK to let Railway's healthcheck pass
        if not request.app.get('init_ok', False):
            return web.json_response({
                "status": "initializing",
                "timestamp": datetime.now().isoformat(),
                "message": "Application is starting up"
            })

        # Check database connection
        db_status = "ok"
        db_error = None
        try:
            # Execute simple query to test connection
            await request.app['db'].execute("SELECT 1")
        except Exception as e:
            db_status = "error"
            db_error = str(e)
            logger.error(f"Database health check failed: {e}")

        # Check webhook status
        webhook_status = "ok"
        webhook_error = None
        try:
            webhook_info = await request.app['bot'].get_webhook_info()
            if not webhook_info.url:
                webhook_status = "error"
                webhook_error = "Webhook not set"
        except Exception as e:
            webhook_status = "error"
            webhook_error = str(e)
            logger.error(f"Webhook health check failed: {e}")

        response = {
            "status": "ok" if db_status == "ok" else "error",  # Only fail on DB errors during runtime
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": {
                    "status": db_status,
                    "error": db_error
                },
                "webhook": {
                    "status": webhook_status,
                    "error": webhook_error
                }
            },
            "startup_phase": request.app['init_ok'],
            "uptime": str(datetime.now() - request.app['start_time'])
        }

        # During runtime, only return 503 for database errors
        status_code = 200 if db_status == "ok" else 503
        return web.json_response(response, status=status_code)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return web.json_response({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status=503)

async def logs_handler(request):
    """Endpoint to get recent application logs"""
    return json_response({
        "logs": [f"[{log['timestamp']}] {log['level']}: {log['message']}" 
                for log in application_logs]
    })

async def init_status_handler(request):
    """Endpoint to get initialization status"""
    # Create a copy with serializable datetime
    init_status = initialization_status.copy()
    if init_status['start_time']:
        init_status['start_time'] = init_status['start_time'].isoformat() if isinstance(init_status['start_time'], datetime) else init_status['start_time']
    return json_response(init_status)

async def update_app_state(key: str, value: any) -> None:
    """Update application state in an async-safe way"""
    global app
    if app:
        app[key] = value

async def on_startup(dp):
    """Startup handler with better status tracking"""
    global app
    log_with_storage(logging.INFO, "Starting initialization process...")
    try:
        initialization_status['start_time'] = datetime.now()
        
        # FIRST: Check environment variables
        log_with_storage(logging.INFO, "Checking environment variables...")
        if not BOT_TOKEN:
            initialization_status['env_status'] = 'Missing BOT_TOKEN'
            log_with_storage(logging.ERROR, "BOT_TOKEN environment variable is not set!")
            raise ValueError("BOT_TOKEN environment variable is not set!")
        initialization_status['env_status'] = 'OK'
        
        # Initialize database
        log_with_storage(logging.INFO, "Initializing database...")
        try:
            await db.connect()  # Make sure this is awaited if it's async
            initialization_status['db_status'] = 'OK'
            log_with_storage(logging.INFO, "Database initialization successful")
        except Exception as e:
            initialization_status['db_status'] = f'Failed: {str(e)}'
            log_with_storage(logging.ERROR, f"Database initialization failed: {str(e)}")
            raise

        # Delete any existing webhook to ensure clean state
        await bot.delete_webhook()
        log_with_storage(logging.INFO, "Cleared existing webhook configuration")
        
        # Set webhook AFTER database is ready
        log_with_storage(logging.INFO, "Setting up webhook...")
        webhook_url = f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}/webhook"
        await bot.set_webhook(webhook_url, drop_pending_updates=True)
        
        # Store webhook URL for fallback
        initialization_status['webhook_url'] = webhook_url
        
        # Mark as initialized if everything is OK
        initialization_status['initialized'] = True
        await update_app_state('init_ok', True)
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
    global app
    # Get port from environment or use default
    port = int(os.getenv('PORT', 8080))
    
    # Log startup information
    log_with_storage(logging.INFO, f"🚀 Starting server on port {port}")
    log_with_storage(logging.INFO, f"Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
    
    # Setup the web app with ALL routes upfront
    app = web.Application()
    
    # Initialize app state
    app['start_time'] = datetime.now()
    app['init_ok'] = False
    app['db'] = db
    app['bot'] = bot
    
    # Add all endpoints
    app.router.add_get('/health', health_handler)
    app.router.add_get('/health/logs', logs_handler)
    app.router.add_get('/health/init', init_status_handler)
    
    # Setup webhook route
    webhook_path = '/webhook'
    async def handle_webhook(request):
        update = await request.json()
        await dp.process_update(update)
        return web.Response()
    
    app.router.add_post(webhook_path, handle_webhook)
    
    # Add startup and shutdown handlers
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # Start the web app
    try:
        web.run_app(
            app,
            host='0.0.0.0',
            port=port,
            access_log=None  # Disable access logs to reduce noise
        )
    except Exception as e:
        log_with_storage(logging.ERROR, f"❌ Server startup failed: {e}")
        raise

if __name__ == "__main__":
    main()
