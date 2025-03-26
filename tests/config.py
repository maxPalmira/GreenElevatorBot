"""
Test configuration module.
Last Updated: 2024-03-20
Changes:
- Added proper database initialization
- Fixed test database cleanup
- Added test admin IDs
"""

import os
import logging
import tempfile
import sqlite3
from dotenv import load_dotenv
from src.utils.db.init_db import init_test_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Load test environment variables
load_dotenv('.env.test', override=True)

# Test configuration
TEST_ADMIN_IDS = [12345]  # Test admin user IDs
TEST_DB_PATH = os.path.join(tempfile.gettempdir(), 'test_bot.db')

def cleanup_test_db():
    """Clean up test database"""
    try:
        if os.path.exists(TEST_DB_PATH):
            os.unlink(TEST_DB_PATH)
    except Exception as e:
        print(f"Error cleaning up test database: {e}")

def setup_test_db():
    """Set up test database"""
    cleanup_test_db()  # Ensure clean state
    db = init_test_db(TEST_DB_PATH)
    return db

def get_test_db():
    """Get test database connection"""
    if not os.path.exists(TEST_DB_PATH):
        return setup_test_db()
    
    try:
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        
        # Verify schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        required_tables = ['users', 'categories', 'products', 'orders', 'cart', 'questions']
        
        if not all(table in tables for table in required_tables):
            conn.close()
            return setup_test_db()
            
        return conn
    except Exception as e:
        print(f"Error connecting to test database: {e}")
        return setup_test_db()

# Test bot token (can be the same as production for now)
TEST_BOT_TOKEN = os.getenv("BOT_TOKEN") 