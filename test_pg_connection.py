#!/usr/bin/env python3
"""
Simple script to test PostgreSQL connection to Railway.
"""

import os
import sys
import logging
import time
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

def test_connection(max_retries=3, timeout=10):
    """Test connection to PostgreSQL database with retries"""
    # Try both connection strings
    conn_string = os.getenv("DATABASE_URL")
    public_conn_string = os.getenv("DATABASE_PUBLIC_URL", conn_string)
    
    if not conn_string:
        logger.error("No DATABASE_URL environment variable found.")
        return False
    
    # Try public URL first
    logger.info("Trying PUBLIC connection string first...")
    if public_conn_string and public_conn_string != conn_string:
        logger.info(f"Public connection string (masked): {public_conn_string.split('@')[0].split(':')[0]}:***@{public_conn_string.split('@')[1]}")
        if try_connect(public_conn_string, max_retries, timeout):
            return True
        logger.info("Public connection failed, trying internal connection...")
    
    # Try internal URL next
    logger.info(f"Internal connection string (masked): {conn_string.split('@')[0].split(':')[0]}:***@{conn_string.split('@')[1]}")
    return try_connect(conn_string, max_retries, timeout)

def try_connect(conn_string, max_retries=3, timeout=10):
    """Try to connect to the database with the given connection string"""
    logger.info(f"Will attempt to connect {max_retries} times with {timeout}s timeout")
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Connection attempt {attempt}/{max_retries}...")
            start_time = time.time()
            conn = psycopg2.connect(conn_string, connect_timeout=timeout)
            
            # Get PostgreSQL version
            cursor = conn.cursor(cursor_factory=DictCursor)
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
            elapsed = time.time() - start_time
            logger.error(f"Attempt {attempt} failed after {elapsed:.2f}s: {e}")
            if attempt < max_retries:
                retry_wait = min(5, timeout / 2)
                logger.info(f"Waiting {retry_wait}s before next attempt...")
                time.sleep(retry_wait)
    
    logger.error(f"Failed to connect after {max_retries} attempts")
    return False

if __name__ == "__main__":
    logger.info("Starting PostgreSQL connection test...")
    result = test_connection(max_retries=3, timeout=15)
    if result:
        logger.info("TEST PASSED: Successfully connected to PostgreSQL database")
        sys.exit(0)
    else:
        logger.error("TEST FAILED: Could not connect to PostgreSQL database")
        sys.exit(1) 