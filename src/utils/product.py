"""
Product utility functions for the Green Elevator Wholesale Bot.
"""

from typing import Dict, Any, Optional
from src.utils.db import Database

def get_product_details(db: Database, product_id: int) -> Optional[Dict[str, Any]]:
    """
    Get product details from the database.
    
    Args:
        db: Database instance
        product_id: ID of the product
        
    Returns:
        Dict with product details or None if not found
    """
    query = "SELECT * FROM products WHERE id = %s"
    result = db.fetchone(query, (product_id,))
    
    if not result:
        return None
        
    return {
        "id": result[0],
        "name": result[1],
        "description": result[2],
        "price": result[3],
        "photo": result[4],
        "category_id": result[5]
    } 