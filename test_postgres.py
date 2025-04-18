#!/usr/bin/env python3
"""
Script to test PostgreSQL database connection.
Created: 2025-04-09
Description: This script tests the connection to PostgreSQL and verifies basic functionality.
"""

import os
import logging
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import DictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_connection(connection_string=None):
    """Test connection to PostgreSQL database"""
    # Get connection string
    conn_string = connection_string or os.getenv("DATABASE_URL")
    if not conn_string:
        logger.error("No DATABASE_URL environment variable found.")
        logger.error("Please set DATABASE_URL in your .env file or Railway environment.")
        return False
    
    # Test connection
    try:
        logger.info("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Get PostgreSQL version
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        if db_version and db_version[0]:
            logger.info(f"Connected to PostgreSQL: {db_version[0]}")
        else:
            logger.info("Connected to PostgreSQL but couldn't get version information")
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        logger.info("Connection test passed!")
        return True
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        return False

def verify_database_structure():
    """Verify database structure"""
    # Get connection string
    conn_string = os.getenv("DATABASE_URL")
    if not conn_string:
        logger.error("No DATABASE_URL environment variable found.")
        return False
    
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Check if tables exist
        logger.info("Checking if tables exist...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if not tables:
            logger.warning("No tables found in database.")
            return False
        
        logger.info("Tables in database:")
        for table in tables:
            logger.info(f"- {table[0]}")
        
        # Check specific tables
        required_tables = ['users', 'categories', 'products', 'cart', 'orders', 'order_items']
        existing_tables = [t[0] for t in tables]
        
        missing_tables = [t for t in required_tables if t not in existing_tables]
        if missing_tables:
            logger.warning(f"Missing tables: {', '.join(missing_tables)}")
        else:
            logger.info("All required tables exist.")
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        return len(missing_tables) == 0
    except psycopg2.Error as e:
        logger.error(f"Error verifying database structure: {e}")
        return False

def test_basic_operations():
    """Test basic database operations"""
    # Get connection string
    conn_string = os.getenv("DATABASE_URL")
    if not conn_string:
        logger.error("No DATABASE_URL environment variable found.")
        return False
    
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Insert a test user
        logger.info("Testing insert operation...")
        test_user_id = 999999999  # Use a very large ID unlikely to conflict
        test_username = "test_user_" + str(test_user_id)
        
        cursor.execute(
            "INSERT INTO users (user_id, username, role) VALUES (%s, %s, %s) " +
            "ON CONFLICT (user_id) DO UPDATE SET username = %s",
            (test_user_id, test_username, 'user', test_username)
        )
        conn.commit()
        
        # Verify the user was inserted
        cursor.execute("SELECT username, role FROM users WHERE user_id = %s", (test_user_id,))
        user = cursor.fetchone()
        
        if user and user['username'] == test_username:
            logger.info("Insert operation successful.")
        else:
            logger.error("Insert operation failed.")
            return False
        
        # Test update operation
        logger.info("Testing update operation...")
        cursor.execute(
            "UPDATE users SET role = %s WHERE user_id = %s",
            ('admin', test_user_id)
        )
        conn.commit()
        
        # Verify the update
        cursor.execute("SELECT role FROM users WHERE user_id = %s", (test_user_id,))
        updated_user = cursor.fetchone()
        
        if updated_user and updated_user['role'] == 'admin':
            logger.info("Update operation successful.")
        else:
            logger.error("Update operation failed.")
            return False
        
        # Test delete operation
        logger.info("Testing delete operation...")
        cursor.execute("DELETE FROM users WHERE user_id = %s", (test_user_id,))
        conn.commit()
        
        # Verify the delete
        cursor.execute("SELECT 1 FROM users WHERE user_id = %s", (test_user_id,))
        deleted_user = cursor.fetchone()
        
        if not deleted_user:
            logger.info("Delete operation successful.")
        else:
            logger.error("Delete operation failed.")
            return False
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        logger.info("Basic operations test passed!")
        return True
    except psycopg2.Error as e:
        logger.error(f"Error testing basic operations: {e}")
        return False

def main():
    """Main function"""
    # Test database connection
    if not test_connection():
        logger.error("Connection test failed. Exiting.")
        sys.exit(1)
    
    # Verify database structure
    if not verify_database_structure():
        logger.warning("Database structure verification incomplete.")
        logger.info("You may need to run the application to create tables.")
        
        # Ask if user wants to continue
        response = input("Continue with basic operation tests? (y/n): ").lower()
        if response != 'y':
            sys.exit(1)
    
    # Test basic operations
    if not test_basic_operations():
        logger.error("Basic operations test failed. Exiting.")
        sys.exit(1)
    
    logger.info("All tests passed! PostgreSQL database is working correctly.")

if __name__ == "__main__":
    main() 