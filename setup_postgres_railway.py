#!/usr/bin/env python3
"""
PostgreSQL Setup Script for Railway Deployment
This script guides the user through setting up a PostgreSQL database on Railway.
Changes:
- Complete rewrite to focus exclusively on PostgreSQL setup
- Added detailed instructions for Railway integration
- Added database schema creation
"""

import sys
import os
import logging
import argparse
import time
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n[{step}] {description}")
    print("-" * 80)

def get_railway_status():
    """Check if Railway CLI is installed and user is logged in"""
    try:
        import subprocess
        # Check if Railway CLI is installed
        process = subprocess.run(["railway", "--version"], capture_output=True, text=True)
        version = process.stdout.strip()
        
        # Check if user is logged in
        process = subprocess.run(["railway", "whoami"], capture_output=True, text=True)
        user_info = process.stdout.strip()
        
        if "not logged in" in user_info.lower():
            return False, f"Railway CLI {version} is installed, but you're not logged in."
        
        return True, f"Railway CLI {version} is installed. Logged in as {user_info}."
    except FileNotFoundError:
        return False, "Railway CLI is not installed."
    except Exception as e:
        return False, f"Error checking Railway status: {e}"

def guide_railway_setup():
    """Guide the user through setting up a PostgreSQL database on Railway"""
    print_header("Railway PostgreSQL Setup Guide")
    
    # Check if Railway CLI is installed and user is logged in
    railway_ok, message = get_railway_status()
    print(message)
    
    if not railway_ok:
        print_step("1", "Install Railway CLI and Log In")
        print("""
To install Railway CLI, run:

npm install -g @railway/cli

Then log in:

railway login

Follow the browser prompts to authenticate your account.
""")
        input("Press Enter when you've completed this step...")
    
    print_step("2", "Create a New PostgreSQL Database on Railway")
    print("""
To create a new PostgreSQL database:

1. Go to the Railway dashboard: https://railway.app/dashboard
2. Select your project or create a new one
3. Click "New" and select "Database" → "PostgreSQL"
4. Wait for the database to be provisioned

Alternatively, you can use Railway CLI:

railway add
""")
    input("Press Enter when you've completed this step...")
    
    print_step("3", "Link Your Project")
    print("""
If you haven't linked your project folder yet:

railway link
""")
    input("Press Enter when you've completed this step...")
    
    print_step("4", "Set Environment Variables")
    print("""
Railway automatically sets the DATABASE_URL variable for your application.
Make sure your application uses this variable to connect to the database.

You can view all variables with:

railway variables

Make sure to add your BOT_TOKEN to Railway:

railway variables --set "BOT_TOKEN=your_bot_token_here"
""")
    input("Press Enter when you've completed this step...")
    
    print_step("5", "Test Database Connection")
    print("""
Run the test script to verify your PostgreSQL connection:

python test_postgres.py

If successful, you'll see a message confirming the connection.
""")
    input("Press Enter when you've completed this step...")
    
    print_step("6", "Initialize Database Schema and Sample Data")
    print("""
Run the database check script to create the tables and add sample data if needed:

python check_railway_db.py

This will:
1. Connect to your PostgreSQL database
2. Create tables if they don't exist
3. Add sample categories and products if needed
""")
    input("Press Enter when you've completed this step...")
    
    print_step("7", "Deploy Your Application")
    print("""
Deploy your application to Railway:

railway up

This will deploy your application with the PostgreSQL database connection.
""")
    
    print_header("Setup Complete")
    print("""
You've successfully set up your PostgreSQL database on Railway!

If you encounter any issues, refer to the following resources:
- Railway documentation: https://docs.railway.app/
- PostgreSQL documentation: https://www.postgresql.org/docs/
- Your application's README file

Happy coding!
""")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="PostgreSQL Setup Script for Railway Deployment")
    parser.add_argument("--guide", action="store_true", help="Display the Railway setup guide")
    
    args = parser.parse_args()
    
    if args.guide or len(sys.argv) == 1:
        guide_railway_setup()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 