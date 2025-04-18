"""
Database connection test script
Created: 2024-04-15
Purpose: Test PostgreSQL database connectivity and configuration
"""

import os
import sys
import logging
from dotenv import load_dotenv
from src.utils.db.pg_database import PostgresDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_connection():
    """Test database connection and configuration"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Log Railway environment variables (safely)
        logger.info("Railway Environment Variables:")
        logger.info(f"- RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'not set')}")
        logger.info(f"- DATABASE_TYPE: {os.getenv('DATABASE_TYPE', 'not set')}")
        logger.info(f"- DATABASE_URL format valid: {'Yes' if os.getenv('DATABASE_URL', '').startswith('postgresql://') else 'No'}")
        
        # Check if using Railway's private networking variables
        pg_vars = ['PGUSER', 'PGPASSWORD', 'PGHOST', 'PGPORT', 'PGDATABASE']
        logger.info("\nRailway PostgreSQL Variables:")
        for var in pg_vars:
            logger.info(f"- {var} present: {'Yes' if os.getenv(var) else 'No'}")
            
        # Attempt connection
        logger.info("\nAttempting database connection...")
        db = PostgresDatabase()
        db.connect()
        
        # Test basic query
        with db.pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT current_timestamp;')
                timestamp = cur.fetchone()[0]
                logger.info(f"Successfully executed test query. Server time: {timestamp}")
            db.pool.putconn(conn)
            
        logger.info("Database connection test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False
    
if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1) 