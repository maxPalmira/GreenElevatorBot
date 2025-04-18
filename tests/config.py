"""
Test configuration module.
Last Updated: 2024-08-30
Changes:
- Migrated from SQLite to PostgreSQL for testing
- Updated database initialization and cleanup procedures
- Implemented test database isolation pattern
"""

import os
import logging
import uuid
import psycopg2
from dotenv import load_dotenv
from src.utils.db.pg_database import PostgresDatabase, create_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Load test environment variables
load_dotenv('.env.test', override=True)

# Test configuration
TEST_ADMIN_IDS = [12345]  # Test admin user IDs
TEST_DB_URL = os.getenv("DATABASE_URL", "")

if not TEST_DB_URL:
    raise ValueError("DATABASE_URL must be set for testing")

# Add test suffix to avoid conflicting with production database
BASE_TEST_DB_URL = TEST_DB_URL + "_test"

def get_unique_test_db_url():
    """Generate a unique test database URL"""
    return f"{BASE_TEST_DB_URL}_{uuid.uuid4().hex[:8]}"

def cleanup_test_db(db_url):
    """Clean up test database"""
    try:
        # Connect to PostgreSQL server (not the specific database)
        server_url = db_url.rsplit('/', 1)[0]
        conn = psycopg2.connect(f"{server_url}/postgres")
        conn.autocommit = True
        
        # Get database name from URL
        db_name = db_url.rsplit('/', 1)[1]
        
        with conn.cursor() as cursor:
            # Terminate all connections to the database
            cursor.execute(f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{db_name}' AND pid <> pg_backend_pid()")
            # Drop the database if it exists
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        
        conn.close()
    except Exception as e:
        print(f"Error cleaning up test database: {e}")

def setup_test_db():
    """Set up test database"""
    db_url = get_unique_test_db_url()
    db = PostgresDatabase(db_url)
    
    # Create database and tables
    try:
        create_db(db_url)
        db.connect()
        
        # Insert test data here
        # This is a simplified version - you may need to add more test data
        
        return db
    except Exception as e:
        print(f"Error setting up test database: {e}")
        cleanup_test_db(db_url)
        raise

def get_test_db():
    """Get a connection to a fresh test database"""
    return setup_test_db()

# Test bot token (can be the same as production for now)
TEST_BOT_TOKEN = os.getenv("BOT_TOKEN") 