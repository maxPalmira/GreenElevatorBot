"""
Database utility class for SQLite operations.
Last Updated: 2024-03-20
Changes:
- Added categories table creation
- Added user_id column to cart table
- Fixed cursor typing
- Added proper error handling for database operations
- Added logging for database operations
"""

import sqlite3
import logging
from typing import Any, List, Optional, Tuple, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, path: Union[str, Path]):
        self.path = str(path)
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def connect(self) -> None:
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(self.path)
            self.cursor = self.conn.cursor()
            self._init_tables()
            logger.info(f"Connected to database: {self.path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def _init_tables(self) -> None:
        """Initialize database tables"""
        if not self.conn or not self.cursor:
            raise RuntimeError("Database not connected")

        try:
            # Create users table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
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
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Create cart table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS cart (
                    user_id INTEGER NOT NULL,
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
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
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

            self.conn.commit()
            logger.info("Database tables initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Error initializing tables: {e}")
            raise

    def execute(self, sql: str, parameters: Optional[Union[Tuple, List[Tuple]]] = None,
                fetchone: bool = False, fetchall: bool = False, commit: bool = False) -> Any:
        """Execute SQL query with parameters"""
        if not self.conn or not self.cursor:
            self.connect()

        assert self.cursor is not None, "Database cursor is not initialized"
        assert self.conn is not None, "Database connection is not initialized"

        try:
            if parameters is None:
                logger.debug(f"Execute query: {sql}")
                self.cursor.execute(sql)
            else:
                logger.debug(f"Execute query with params: {sql}, {parameters}")
                self.cursor.execute(sql, parameters)

            if commit:
                self.conn.commit()

            if fetchone:
                return self.cursor.fetchone()
            if fetchall:
                return self.cursor.fetchall()
            return None

        except sqlite3.Error as e:
            logger.error(f"Error executing query: {e}")
            raise

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            logger.info("Database connection closed")

    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close()

    def get_user_role(self, user_id: int) -> str:
        """Get user role from database"""
        result = self.execute(
            'SELECT role FROM users WHERE user_id = ?',
            (user_id,),
            fetchone=True
        )
        return result[0] if result else 'user'

    def set_user_role(self, user_id: int, role: str) -> bool:
        """Set user role in database"""
        try:
            self.execute(
                'INSERT OR REPLACE INTO users (user_id, role) VALUES (?, ?)',
                (user_id, role),
                commit=True
            )
            return True
        except sqlite3.Error:
            return False

    def get_products_with_categories(self) -> List[Tuple]:
        """Get all products with their category information"""
        return self.execute('''
            SELECT p.idx, p.title, p.body, p.image, p.price, p.tag, c.title as category
            FROM products p
            LEFT JOIN categories c ON p.tag = c.idx
            ORDER BY p.title
        ''', fetchall=True)

def create_db(path: Union[str, Path]) -> None:
    """Create and initialize database"""
    db = Database(path)
    db.connect()
    
    # Add categories
    categories = [
        ('premium', '🔥 Premium Strains'),
        ('hybrid', '🌿 Hybrid Strains'),
        ('bulk', '📦 Bulk Deals')
    ]
    
    for idx, title in categories:
        db.execute('INSERT OR IGNORE INTO categories VALUES (?, ?)', (idx, title))
    
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
        db.execute('INSERT OR IGNORE INTO products (idx, title, body, image, price, tag, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (idx, title, body, image, price, tag, user_id))

if __name__ == '__main__':
    create_db() 