"""Test configuration module"""
import os
import logging
from dotenv import load_dotenv
from src.utils.db.init_db import init_test_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Load test environment variables
load_dotenv('.env.test', override=True)

# Test database path
TEST_DB_PATH = "test_database.db"

# Test bot token (can be the same as production for now)
TEST_BOT_TOKEN = os.getenv("BOT_TOKEN")

# Test admin IDs
TEST_ADMIN_IDS = [123456789]  # Test user ID

def setup_test_db():
    """Initialize test database"""
    return init_test_db(TEST_DB_PATH)

# Clean up function
def cleanup_test_db():
    """Remove test database if it exists"""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH) 