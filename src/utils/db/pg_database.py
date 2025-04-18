"""
PostgreSQL Database utility class.
Created: 2025-04-09
Description: PostgreSQL database implementation replacing SQLite
Changes:
- Fixed connection string priority for local development
- Simplified connection logic
"""

import os
import logging
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import DictCursor
from typing import Any, List, Optional, Tuple, Union, Dict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class PostgresDatabase:
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize database with connection string"""
        # Use provided connection string first, then DATABASE_URL, then construct from PG* vars
        self.connection_string = connection_string or os.getenv('DATABASE_URL')
        
        # If no connection string and we're in Railway, construct from PG* vars
        if not self.connection_string and os.getenv('RAILWAY_ENVIRONMENT') and all(os.getenv(var) for var in ['PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE']):
            self.connection_string = (
                f"postgresql://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@"
                f"{os.getenv('PGHOST')}:{os.getenv('PGPORT')}/{os.getenv('PGDATABASE')}"
            )
            logger.info("Using Railway private networking configuration")
        else:
            logger.info("Using provided connection string or DATABASE_URL")
            
        self.pool = None
        self.conn = None
        self.cursor = None
        
        if not self.connection_string:
            raise ValueError("No database connection string provided")
            
        # Parse and validate connection string
        try:
            parsed = urlparse(self.connection_string)
            # Log connection details safely (without credentials)
            logger.info(f"Database connection details:")
            logger.info(f"- Host: {parsed.hostname}")
            logger.info(f"- Port: {parsed.port}")
            logger.info(f"- Database: {parsed.path[1:] if parsed.path else 'default'}")
            logger.info(f"- Username present: {'Yes' if parsed.username else 'No'}")
            logger.info(f"- Password present: {'Yes' if parsed.password else 'No'}")
        except Exception as e:
            logger.error(f"Invalid connection string format: {str(e)}")
            raise ValueError("Invalid database connection string format")

    def connect(self) -> None:
        """Create connection pool and test connection"""
        try:
            logger.info("Attempting to create database connection pool...")
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=20,
                dsn=self.connection_string
            )
            
            # Test connection
            with self.pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT version();')
                    version = cur.fetchone()[0]
                    logger.info(f"Successfully connected to PostgreSQL: {version}")
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            if self.pool:
                self.pool.closeall()
                self.pool = None
            raise

    def _get_connection(self):
        """Get a connection from the pool"""
        if not self.pool:
            self.connect()
        if not self.pool:
            raise RuntimeError("Database connection pool not initialized")
        return self.pool.getconn()

    def _return_connection(self, conn):
        """Return a connection to the pool"""
        if self.pool and conn:
            self.pool.putconn(conn)

    def _init_tables(self) -> None:
        """Initialize database tables - PostgreSQL version"""
        if not self.conn or not self.cursor:
            raise RuntimeError("Database not connected")

        try:
            # Create users table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create categories table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    idx TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create products table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    idx TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    body TEXT,
                    image TEXT,
                    price INTEGER NOT NULL,
                    tag TEXT,
                    user_id BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Create cart table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS cart (
                    user_id BIGINT NOT NULL,
                    product_id TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (product_id) REFERENCES products(idx),
                    PRIMARY KEY (user_id, product_id)
                )
            ''')

            # Create orders table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    shipping_address TEXT,
                    total_amount INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Create order_items table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    order_id INTEGER,
                    product_id TEXT,
                    quantity INTEGER,
                    price INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders(order_id),
                    FOREIGN KEY (product_id) REFERENCES products(idx),
                    PRIMARY KEY (order_id, product_id)
                )
            ''')

            # Create indexes
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_tag ON products(tag)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_cart_user_id ON cart(user_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)')

            self.conn.commit()
            logger.info("PostgreSQL database tables initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"Error initializing tables: {e}")
            raise

    def execute(self, sql: str, parameters: Optional[Union[Tuple, Dict, List[Tuple]]] = None,
                fetchone: bool = False, fetchall: bool = False, commit: bool = False) -> Any:
        """Execute SQL query with parameters"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=DictCursor)
            
            if parameters is None:
                logger.debug(f"Execute query: {sql}")
                cursor.execute(sql)
            else:
                logger.debug(f"Execute query with params: {sql}, {parameters}")
                cursor.execute(sql, parameters)

            if commit:
                conn.commit()

            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()
            return None

        except psycopg2.Error as e:
            logger.error(f"Error executing query: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self._return_connection(conn)

    def close(self) -> None:
        """Close all database connections in the pool"""
        if self.pool:
            self.pool.closeall()
            self.pool = None
            logger.info("PostgreSQL database connection pool closed")

    def __del__(self):
        """Destructor to ensure connection pool is closed"""
        self.close()

    def get_user_role(self, user_id: int) -> str:
        """Get user role from database"""
        result = self.execute(
            'SELECT role FROM users WHERE user_id = %s',
            (user_id,),
            fetchone=True
        )
        return result[0] if result else 'user'

    def set_user_role(self, user_id: int, role: str) -> bool:
        """Set user role in database"""
        try:
            self.execute(
                'INSERT INTO users (user_id, role) VALUES (%s, %s) ' +
                'ON CONFLICT (user_id) DO UPDATE SET role = %s',
                (user_id, role, role),
                commit=True
            )
            return True
        except Exception:
            return False

    def get_products_with_categories(self) -> List:
        """Get all products with their category information"""
        return self.execute('''
            SELECT p.idx, p.title, p.body, p.image, p.price, p.tag, c.title as category
            FROM products p
            LEFT JOIN categories c ON p.tag = c.idx
            ORDER BY p.title
        ''', fetchall=True)

def create_db(connection_string: Optional[str] = None) -> None:
    """Create and initialize PostgreSQL database"""
    db = PostgresDatabase(connection_string)
    db.connect()
    
    # Add categories
    categories = [
        ('premium', '🔥 Premium Strains'),
        ('hybrid', '🌿 Hybrid Strains'),
        ('bulk', '📦 Bulk Deals')
    ]
    
    for idx, title in categories:
        db.execute(
            'INSERT INTO categories (idx, title) VALUES (%s, %s) ' +
            'ON CONFLICT (idx) DO NOTHING',
            (idx, title),
            commit=True
        )
    
    # Add products with user_id
    products = [
        # Premium Strains
        ('thai_premium', 'Premium Thai', '''Our signature Thai strain, carefully cultivated for maximum potency and flavor. Perfect for premium market segments.

• Effects: Energetic, Creative, Focused
• Type: Sativa-dominant
• Cultivation: Indoor''',
         'https://i.ibb.co/VqFgzVk/product1-1.jpg', 99000, 'premium', None),
        
        # Hybrid Strains
        ('island_blend', 'Island Blend', '''A unique blend of island-grown strains, offering a perfect balance of effects. Ideal for diverse customer preferences.

• Effects: Balanced, Smooth, Versatile
• Type: Hybrid
• Cultivation: Indoor/Outdoor''',
         'https://i.ibb.co/0MdRHKd/product2-1.jpg', 99000, 'hybrid', None),
        
        # Bulk Deals
        ('royal_haze', 'Royal Haze', '''Our premium haze variety, known for its exceptional quality and consistent effects. A top choice for discerning customers.

• Effects: Uplifting, Clear, Long-lasting
• Type: Sativa
• Cultivation: Indoor''',
         'https://i.ibb.co/C2Lx9Lq/product3-1.jpg', 99000, 'bulk', None)
    ]
    
    for idx, title, body, image, price, tag, user_id in products:
        db.execute(
            '''INSERT INTO products (idx, title, body, image, price, tag, user_id) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (idx) DO NOTHING''',
            (idx, title, body, image, price, tag, user_id),
            commit=True
        )

if __name__ == '__main__':
    create_db() 