"""
Created: 2024-03-20
Last Updated: 2024-03-20
Description: Database initialization module
Changes:
- Updated test database initialization to match catalog handler schema
- Added user_id column to product inserts
- Fixed test data to include proper user_id values
"""

import os
import logging
from typing import Optional
from src.utils.db.database import Database
from src.config import DATABASE_PATH

# Get logger
logger = logging.getLogger(__name__)

def init_test_db(db_path: Optional[str] = None) -> Database:
    """Initialize test database with sample data"""
    # Suppress SQL query logging during tests
    if 'pytest' in os.environ:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

    # Create database instance
    db = Database(db_path or DATABASE_PATH)
    db.connect()

    try:
        # Insert test user
        db.execute(
            'INSERT OR REPLACE INTO users (user_id, username, role) VALUES (?, ?, ?)',
            (12345, 'test_user', 'user'),
            commit=True
        )

        # Insert test categories
        categories = [
            ('cat1', 'Category 1'),
            ('cat2', 'Category 2'),
            ('cat3', 'Category 3')
        ]
        for idx, title in categories:
            db.execute(
                'INSERT OR REPLACE INTO categories (idx, title) VALUES (?, ?)',
                (idx, title),
                commit=True
            )

        # Insert test products with user_id
        products = [
            ('prod1', 'Test Product 1', 'Description 1', 'image1.jpg', 1000, 'cat1', 12345),
            ('prod2', 'Test Product 2', 'Description 2', 'image2.jpg', 2000, 'cat2', 12345),
            ('prod3', 'Test Product 3', 'Description 3', 'image3.jpg', 3000, 'cat3', 12345)
        ]
        for idx, title, body, image, price, tag, user_id in products:
            db.execute(
                '''INSERT OR REPLACE INTO products 
                   (idx, title, body, image, price, tag, user_id) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (idx, title, body, image, price, tag, user_id),
                commit=True
            )

        logger.info("Test database initialized successfully")
        return db

    except Exception as e:
        logger.error(f"Error initializing test database: {e}")
        raise

# Create database instance
db = Database(DATABASE_PATH)

def init_db(db_path: Optional[str] = None) -> Database:
    """Initialize production database with default data"""
    db = Database(db_path or DATABASE_PATH)
    db.connect()

    try:
        # Insert default categories
        categories = [
            ('premium', '🔥 Premium Strains'),
            ('hybrid', '🌿 Hybrid Strains'),
            ('bulk', '📦 Bulk Deals')
        ]
        for idx, title in categories:
            db.execute(
                'INSERT OR IGNORE INTO categories (idx, title) VALUES (?, ?)',
                (idx, title),
                commit=True
            )

        # Insert default products with user_id
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
                '''INSERT OR IGNORE INTO products 
                   (idx, title, body, image, price, tag, user_id) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (idx, title, body, image, price, tag, user_id),
                commit=True
            )

        logger.info("Production database initialized successfully")
        return db

    except Exception as e:
        logger.error(f"Error initializing production database: {e}")
        raise

if __name__ == '__main__':
    init_db() 