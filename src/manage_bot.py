#!/usr/bin/env python3
import os
import sys
import time
import logging
import subprocess
import signal
import asyncio
from aiogram import Bot
from config import LOGS_DIR, BOT_TOKEN

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'process.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
PID_FILE = 'run/bot.pid'
PYTHON_PATH = sys.executable
APP_PATH = os.path.join('src', 'app.py')

def get_bot_process():
    """Get running bot process if any"""
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)  # Check if process exists
                return pid
            except OSError:
                pass
            # Clean up stale PID file
            os.remove(PID_FILE)
    except (FileNotFoundError, ValueError):
        pass
    return None

async def reset_webhook():
    """Reset webhook settings"""
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.delete_webhook()
        webhook_info = await bot.get_webhook_info()
        logger.info(f"Webhook status: {webhook_info}")
        await bot.close()
    except Exception as e:
        logger.error(f"Error resetting webhook: {e}")

def stop_bot():
    """Stop the bot process"""
    pid = get_bot_process()
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            logger.info(f"Sent SIGTERM to bot process {pid}")
            
            # Wait for process to stop
            for _ in range(10):  # Wait up to 10 seconds
                try:
                    os.kill(pid, 0)
                    time.sleep(1)
                except OSError:
                    break
            
            # Force kill if still running
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
                logger.info(f"Sent SIGKILL to bot process {pid}")
            except OSError:
                pass
            
            logger.info(f"Bot process {pid} stopped")
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
            return True
        except ProcessLookupError:
            logger.info("Bot process already stopped")
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
    return False

def start_bot():
    """Start the bot process"""
    # Stop any existing process
    stop_bot()
    
    try:
        # Start bot as a new process
        with open(os.path.join(LOGS_DIR, 'process.log'), "w") as log_file:
            process = subprocess.Popen(
                [PYTHON_PATH, "-u", APP_PATH],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True  # Create new process group
            )
        
        # Save PID
        with open(PID_FILE, "w") as f:
            f.write(str(process.pid))
        
        logger.info(f"Bot started with PID {process.pid}")
        return True
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return False

def restart_bot():
    """Restart the bot process"""
    stop_bot()
    return start_bot()

def check_status():
    """Check bot status"""
    pid = get_bot_process()
    if pid:
        logger.info(f"Bot is running with PID {pid}")
        return True
    else:
        logger.info("Bot is not running")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python manage_bot.py [start|stop|restart|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        if start_bot():
            sys.exit(0)
        sys.exit(1)
    elif command == "stop":
        if stop_bot():
            sys.exit(0)
        sys.exit(1)
    elif command == "restart":
        if restart_bot():
            sys.exit(0)
        sys.exit(1)
    elif command == "status":
        if check_status():
            sys.exit(0)
        sys.exit(1)
    else:
        print("Invalid command. Use start, stop, restart, or status")
        sys.exit(1) 