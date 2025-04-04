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

# Colors for console output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_color(text, color):
    """Print colored text to console"""
    print(f"{color}{text}{Colors.ENDC}")

def check_telegram_webhook(token):
    """Check Telegram webhook status"""
    url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    
    try:
        print_color("Checking Telegram webhook status...", Colors.CYAN)
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            webhook_info = response.json()
            
            if webhook_info.get('ok'):
                result = webhook_info.get('result', {})
                webhook_url = result.get('url', 'Not set')
                pending_updates = result.get('pending_update_count', 0)
                has_custom_cert = result.get('has_custom_certificate', False)
                last_error_date = result.get('last_error_date')
                last_error_message = result.get('last_error_message', 'None')
                
                print_color("\n=== TELEGRAM WEBHOOK STATUS ===", Colors.BOLD + Colors.BLUE)
                print_color(f"URL: {webhook_url}", Colors.CYAN if webhook_url else Colors.RED)
                print_color(f"Pending updates: {pending_updates}", Colors.YELLOW if pending_updates > 0 else Colors.GREEN)
                print_color(f"Custom certificate: {has_custom_cert}", Colors.YELLOW if has_custom_cert else Colors.GREEN)
                
                if last_error_date:
                    error_time = datetime.fromtimestamp(last_error_date).strftime('%Y-%m-%d %H:%M:%S')
                    print_color(f"Last error: {error_time} - {last_error_message}", Colors.RED)
                else:
                    print_color("No webhook errors reported", Colors.GREEN)
                    
                return True, webhook_url
            else:
                print_color(f"Error getting webhook info: {webhook_info.get('description')}", Colors.RED)
                return False, None
        else:
            print_color(f"Error checking webhook: HTTP {response.status_code}", Colors.RED)
            return False, None
            
    except Exception as e:
        print_color(f"Failed to check webhook: {str(e)}", Colors.RED)
        return False, None

def get_local_version():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except:
        return None

def check_railway_health(base_url):
    """Check the health of the Railway deployment"""
    try:
        response = requests.get(f"{base_url}/health")
        response.raise_for_status()
        health_data = response.json()
        
        print("\n=== RAILWAY HEALTH STATUS ===")
        print(f"Health status: {health_data.get('status', 'Unknown')}")
        
        # Compare versions
        deployed_version = health_data.get('version')
        local_version = get_local_version()
        
        if deployed_version and local_version:
            print(f"\n=== VERSION COMPARISON ===")
            print(f"Deployed version: {deployed_version[:8]}")
            print(f"Local version:    {local_version[:8]}")
            if deployed_version != local_version:
                print(Colors.YELLOW + "WARNING: Local code differs from deployed version!" + Colors.ENDC)
                # Show git diff
                try:
                    diff = subprocess.check_output(['git', 'diff', '--stat', deployed_version]).decode('ascii').strip()
                    if diff:
                        print("\nUndeployed changes:")
                        print(diff)
                except:
                    pass
            else:
                print(Colors.GREEN + "✓ Local code matches deployed version" + Colors.ENDC)
        
        return health_data.get('status') == 'OK'
    except Exception as e:
        print(f"\n=== RAILWAY HEALTH ERROR ===")
        print(f"Error: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Railway Bot Health Checker")
    parser.add_argument("--token", help="Telegram Bot Token")
    args = parser.parse_args()
    
    # Get token from args, env or prompt
    token = args.token or os.getenv('BOT_TOKEN')
    
    if not token:
        token = input("Enter your Telegram Bot Token: ")
        
    if not token:
        print_color("No Telegram Bot Token provided.", Colors.RED)
        sys.exit(1)
    
    # Check webhook first
    success, webhook_url = check_telegram_webhook(token)
    
    if success and webhook_url:
        # Then check health endpoint
        check_railway_health(webhook_url)
    
if __name__ == "__main__":
    main() 