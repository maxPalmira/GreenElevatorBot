"""
Database module for the Telegram bot.
Updated to use PostgreSQL exclusively, removing SQLite support.
Changes:
- Removed SQLite imports and connection logic
- Made PostgreSQL the only database option
- Improved error handling and logging
"""

import os
import logging
import psycopg2
from datetime import datetime
from src.config import DATABASE_URL

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._url = DATABASE_URL
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Establish PostgreSQL database connection"""
        try:
            # PostgreSQL connection
            self.conn = psycopg2.connect(self._url)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            self.logger.error(f"PostgreSQL connection failed: {str(e)}")
            raise

    async def test_connection(self):
        """Test PostgreSQL database connection"""
        try:
            # Test PostgreSQL connection
            with psycopg2.connect(self._url) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return True
        except Exception as e:
            self.logger.error(f"PostgreSQL connection test failed: {str(e)}")
            raise 