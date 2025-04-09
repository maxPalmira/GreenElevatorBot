import os
import logging
import psycopg2
import sqlite3
from datetime import datetime
from src.config import DATABASE_TYPE, DATABASE_URL, DATABASE_PATH

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._type = DATABASE_TYPE
        self._url = DATABASE_URL
        self._path = DATABASE_PATH
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Establish database connection"""
        try:
            if self._type == "postgres":
                # PostgreSQL connection
                self.conn = psycopg2.connect(self._url)
                self.cursor = self.conn.cursor()
            else:
                # SQLite connection
                self.conn = sqlite3.connect(self._path)
                self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            self.logger.error(f"Database connection failed: {str(e)}")
            raise

    async def test_connection(self):
        """Test database connection"""
        try:
            if self._type == "postgres":
                # Test PostgreSQL connection
                with psycopg2.connect(self._url) as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
                        return True
            else:
                # Test SQLite connection
                with sqlite3.connect(self._path) as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT 1")
                    return True
        except Exception as e:
            self.logger.error(f"Database connection test failed: {str(e)}")
            raise 