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
ADMINS = parse_admin_ids(os.getenv("ADMINS", ""))
logger.info(f"Configured admin IDs: {ADMINS}")

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "src", "assets")

# Database
DATABASE_PATH = os.path.join(DATA_DIR, "database.db")

# Ensure directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True) 