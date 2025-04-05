#!/usr/bin/env python3
"""
Created: 2024-03-26
Description: Script to check Railway bot health and status
"""

import os
import sys
import json
import requests
import argparse
from datetime import datetime
import subprocess
from typing import Dict, Any, Optional

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def color_text(text: str, color: str) -> str:
    """Add color to text"""
    return f"{color}{text}{Colors.ENDC}"

def format_status(status: str) -> str:
    """Format status with appropriate color"""
    if status.lower() == "ok":
        return color_text("OK", Colors.GREEN)
    elif status.lower() == "error":
        return color_text("ERROR", Colors.RED)
    else:
        return color_text(status, Colors.YELLOW)

def check_health(base_url: str) -> Dict[str, Any]:
    """Check the main health endpoint"""
    try:
        response = requests.get(f"{base_url}/health")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(color_text(f"Failed to check health: {str(e)}", Colors.RED))
        sys.exit(1)

def get_logs(base_url: str) -> Optional[list]:
    """Get recent application logs"""
    try:
        response = requests.get(f"{base_url}/health/logs")
        response.raise_for_status()
        return response.json().get("logs", [])
    except requests.RequestException:
        return None

def get_init_status(base_url: str) -> Optional[Dict[str, Any]]:
    """Get initialization status"""
    try:
        response = requests.get(f"{base_url}/health/init")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def check_telegram_webhook(token: str) -> Dict[str, Any]:
    """Check Telegram webhook status"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getWebhookInfo")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(color_text(f"Failed to check Telegram webhook: {str(e)}", Colors.RED))
        return {}

def print_section(title: str):
    """Print a section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {title} ==={Colors.ENDC}\n")

def main():
    parser = argparse.ArgumentParser(description="Check Railway deployment health")
    parser.add_argument("--token", help="Telegram bot token")
    parser.add_argument("--url", default="https://greenelevetortelegrambottest-production.up.railway.app",
                      help="Base URL of the Railway deployment")
    args = parser.parse_args()

    # Get bot token from environment if not provided
    token = args.token or os.getenv("BOT_TOKEN")
    if not token:
        print(color_text("No bot token provided. Webhook status will not be checked.", Colors.YELLOW))

    print_section("Railway Deployment Status")
    
    # Check main health endpoint
    health_data = check_health(args.url)
    
    # Print overall status
    status = health_data.get("status", "unknown")
    print(f"Status: {format_status(status)}")
    
    if "version" in health_data:
        print(f"Version: {color_text(health_data['version'][:8], Colors.BLUE)}")
    
    if "uptime" in health_data and health_data["uptime"]:
        print(f"Uptime: {color_text(health_data['uptime'], Colors.BLUE)}")

    # Print initialization status
    print_section("Initialization Status")
    init_status = health_data.get("initialization", {})
    if init_status:
        print(f"Initialized: {format_status('ok' if init_status.get('initialized') else 'error')}")
        print(f"Environment: {format_status(init_status.get('env_status', 'unknown'))}")
        print(f"Database: {format_status(init_status.get('db_status', 'unknown'))}")
        
        if init_status.get("errors"):
            print("\nInitialization Errors:")
            for error in init_status["errors"]:
                print(color_text(f"  - {error}", Colors.RED))

    # Print webhook status
    print_section("Webhook Status")
    webhook_info = health_data.get("webhook", {})
    if webhook_info:
        print(f"URL: {color_text(webhook_info.get('url', 'Not set'), Colors.BLUE)}")
        pending = webhook_info.get("pending_updates", 0)
        print(f"Pending updates: {color_text(str(pending), Colors.YELLOW if pending > 0 else Colors.GREEN)}")
    
    # Get and display recent logs
    print_section("Recent Application Logs")
    logs = get_logs(args.url)
    if logs:
        for log in logs[-10:]:  # Show last 10 logs
            print(log)
    else:
        print(color_text("Could not retrieve application logs", Colors.YELLOW))

    # Check Telegram webhook if token provided
    if token:
        print_section("Telegram API Status")
        telegram_status = check_telegram_webhook(token)
        if telegram_status.get("ok"):
            webhook_info = telegram_status["result"]
            print(f"Webhook URL: {color_text(webhook_info.get('url', 'Not set'), Colors.BLUE)}")
            print(f"Has custom certificate: {webhook_info.get('has_custom_certificate', False)}")
            print(f"Pending updates: {webhook_info.get('pending_update_count', 0)}")
            if webhook_info.get("last_error_date"):
                error_date = datetime.fromtimestamp(webhook_info["last_error_date"])
                print(color_text(f"Last error: {webhook_info.get('last_error_message', 'Unknown')} at {error_date}", Colors.RED))
        else:
            print(color_text("Failed to get Telegram webhook status", Colors.RED))

    # Print suggestions if there are issues
    if status.lower() != "ok" or (init_status and not init_status.get("initialized")):
        print_section("Troubleshooting Suggestions")
        if not init_status.get("initialized"):
            print("- Check the application logs for initialization errors")
            print("- Verify all required environment variables are set")
            print("- Check database connection and configuration")
        if not webhook_info.get("url"):
            print("- Webhook URL is not set, try redeploying the application")
        if pending > 0:
            print(f"- There are {pending} pending updates, consider resetting the webhook")

if __name__ == "__main__":
    main() 