import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

def parse_admin_ids(admin_str):
    """Parse admin IDs from environment string with proper error handling"""
    if not admin_str or admin_str.strip() == "":
        logger.info("No admin IDs configured - bot will run in customer-only mode")
        return []
        
    try:
        # Remove any whitespace and split by comma
        admin_ids = []
        for id_str in admin_str.strip().split(','):
            # Skip empty strings
            if not id_str.strip():
                continue
                
            # Try to find where the ID ends (before any comment or invalid chars)
            clean_id = ''
            for char in id_str.strip():
                if char.isdigit():
                    clean_id += char
                else:
                    break
                    
            if clean_id:
                try:
                    admin_ids.append(int(clean_id))
                    logger.info(f"Added admin ID: {clean_id}")
                except ValueError:
                    logger.warning(f"Skipping invalid admin ID: {id_str}")
            
        return admin_ids
        
    except Exception as e:
        logger.error(f"Error parsing admin IDs: {str(e)}")
        logger.error(f"Raw admin string: {admin_str}")
        logger.warning("Bot will run in customer-only mode due to admin configuration error")
        return []

# List of admin user IDs with proper error handling
raw_admin_ids = os.getenv("ADMINS", "")

# In production, ensure we have at least one admin ID
if os.getenv('RAILWAY_ENVIRONMENT') == 'production' and not raw_admin_ids:
    logger.warning("No admin IDs configured in production - using default admin ID")
    raw_admin_ids = "238038462"  # Default admin ID for production

ADMINS = parse_admin_ids(raw_admin_ids)
logger.info(f"Configured admin IDs: {ADMINS}")

# Ensure we have admin IDs in production
if os.getenv('RAILWAY_ENVIRONMENT') == 'production' and not ADMINS:
    raise ValueError("No valid admin IDs configured for production environment!")

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "src", "assets")

# Database configuration - PostgreSQL only
# Format: postgresql://username:password@hostname:port/database
DATABASE_URL = os.getenv("DATABASE_URL")

# Enforce PostgreSQL configuration
if not DATABASE_URL:
    error_msg = "DATABASE_URL environment variable is not set! PostgreSQL is required."
    logger.error(error_msg)
    raise ValueError(error_msg)

logger.info("Using PostgreSQL database")

# Ensure directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True) 