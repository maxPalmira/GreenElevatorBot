"""
Created: 2024-03-20
Last Updated: 2024-03-20
Description: Database initialization module
Changes:
- Updated test database initialization to match catalog handler schema
"""

import os
import logging
from src.utils.db.database import Database
from src.config import DATABASE_PATH

# Get logger
logger = logging.getLogger(__name__)

def init_test_db(db_path: str) -> Database:
    """Initialize test database with schema and test data"""
    # Suppress SQL query logging during tests
    if 'pytest' in os.environ.get('PYTHONPATH', ''):
        logging.getLogger('utils.db.database').setLevel(logging.WARNING)
    
    # Create database instance
    db = Database(db_path)
    
    # Initialize schema
    db.create_tables()
    
    # Add test data
    db.query('INSERT INTO users (user_id, username, role) VALUES (?, ?, ?)',
             (12345, 'admin', 'admin'))
    
    # Add test categories
    categories = [
        ('cat1', 'Category 1'),
        ('cat2', 'Category 2')
    ]
    for idx, title in categories:
        db.query('INSERT INTO categories VALUES (?, ?)', (idx, title))
    
    # Add test products
    products = [
        ('prod1', 'Test Product 1', 'Description 1', 'image1.jpg', 1000, 'cat1'),
        ('prod2', 'Test Product 2', 'Description 2', None, 2000, 'cat1'),
        ('prod3', 'Test Product 3', 'Description 3', 'image3.jpg', 3000, 'cat2')
    ]
    for idx, title, body, image, price, tag in products:
        db.query('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)',
                (idx, title, body, image, price, tag))
    
    return db

# Create database instance
db = Database(DATABASE_PATH)

def init_db():
    """Initialize the database with default data"""
    global db
    
    # Create tables
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
    init_db() 