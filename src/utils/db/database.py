import sqlite3
import os
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
from src.config import DATABASE_PATH

# Configure logging
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        
        # Suppress logging in test environment
        if 'pytest' in os.environ.get('PYTHONPATH', ''):
            logger.setLevel(logging.WARNING)
        
        # Initialize connection
        self.connect()
    
    def connect(self) -> None:
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
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
            
            data = None
            if commit:
                self.conn.commit()
            if fetchone:
                data = self.cursor.fetchone()
            if fetchall:
                data = self.cursor.fetchall()
                
            return data
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    def query(self, sql: str, parameters: Optional[Tuple] = None, 
              fetchone: bool = False, fetchall: bool = False) -> Any:
        """Execute query with automatic commit"""
        return self.execute(sql, parameters, fetchone=fetchone, fetchall=fetchall, commit=True)

    def execute_many(self, sql: str, parameters: List[Tuple]) -> None:
        """Execute the same query with different parameters"""
        if not self.conn or not self.cursor:
            self.connect()
            
        assert self.cursor is not None, "Database cursor is not initialized"
        assert self.conn is not None, "Database connection is not initialized"
            
        try:
            self.cursor.executemany(sql, parameters)
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error executing many: {str(e)}")
            raise

    def create_tables(self) -> None:
        """Create necessary tables if they don't exist"""
        # Users table
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute(sql, commit=True)
        
        # Categories table
        sql = """
        CREATE TABLE IF NOT EXISTS categories (
            idx TEXT PRIMARY KEY,
            title TEXT NOT NULL
        )
        """
        self.execute(sql, commit=True)
        
        # Products table
        sql = """
        CREATE TABLE IF NOT EXISTS products (
            idx TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            body TEXT,
            image TEXT,
            price INTEGER,
            tag TEXT,
            FOREIGN KEY (tag) REFERENCES categories(idx)
        )
        """
        self.execute(sql, commit=True)
        
        # Orders table
        sql = """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(idx),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """
        self.execute(sql, commit=True)
        
        # Cart table
        sql = """
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(idx),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id, product_id)
        )
        """
        self.execute(sql, commit=True)

        # Questions table
        sql = """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            question TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """
        self.execute(sql, commit=True)

    def get_user_role(self, user_id: int) -> Optional[str]:
        """Get user's role from database"""
        try:
            result = self.execute(
                'SELECT role FROM users WHERE user_id = ?',
                (user_id,),
                fetchone=True
            )
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting user role: {str(e)}")
            return None

    def set_user_role(self, user_id: int, username: str, role: str) -> bool:
        """Set user's role in database"""
        try:
            self.execute(
                '''INSERT INTO users (user_id, username, role) 
                   VALUES (?, ?, ?)
                   ON CONFLICT(user_id) 
                   DO UPDATE SET role = ?''',
                (user_id, username, role, role),
                commit=True
            )
            logger.info(f"Set role '{role}' for user {username} (ID: {user_id})")
            return True
        except Exception as e:
            logger.error(f"Error setting user role: {str(e)}")
            return False

    def get_products_with_categories(self) -> List[Tuple]:
        """Get all products with their category information"""
        return self.query('''
            SELECT p.idx, p.title, p.body, p.image, p.price, p.tag, c.title as category
            FROM products p
            LEFT JOIN categories c ON p.tag = c.idx
            ORDER BY p.title
        ''', fetchall=True)

def create_db() -> None:
    """Create and initialize database"""
    db = Database()
    db.create_tables()
    
    # Add categories
    categories = [
        ('premium', '🔥 Premium Strains'),
        ('hybrid', '🌿 Hybrid Strains'),
        ('bulk', '📦 Bulk Deals')
    ]
    
    for idx, title in categories:
        db.query('INSERT OR IGNORE INTO categories VALUES (?, ?)', (idx, title))
    
    # Add products
    products = [
        # Premium Strains
        ('thai_premium', 'Premium Thai', '''Our signature Thai strain, carefully cultivated for maximum potency and flavor. Perfect for premium market segments.

• Effects: Energetic, Creative, Focused
• Type: Sativa-dominant
• Cultivation: Indoor''',
         'https://i.ibb.co/VqFgzVk/product1-1.jpg', 99000, 'premium'),
        
        # Hybrid Strains
        ('island_blend', 'Island Blend', '''A unique blend of island-grown strains, offering a perfect balance of effects. Ideal for diverse customer preferences.

• Effects: Balanced, Smooth, Versatile
• Type: Hybrid
• Cultivation: Indoor/Outdoor''',
         'https://i.ibb.co/0MdRHKd/product2-1.jpg', 99000, 'hybrid'),
        
        # Bulk Deals
        ('royal_haze', 'Royal Haze', '''Our premium haze variety, known for its exceptional quality and consistent effects. A top choice for discerning customers.

• Effects: Uplifting, Clear, Long-lasting
• Type: Sativa
• Cultivation: Indoor''',
         'https://i.ibb.co/C2Lx9Lq/product3-1.jpg', 99000, 'bulk')
    ]
    
    for idx, title, body, image, price, tag in products:
        db.query('INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?, ?, ?)',
                (idx, title, body, image, price, tag))

if __name__ == '__main__':
    create_db() 