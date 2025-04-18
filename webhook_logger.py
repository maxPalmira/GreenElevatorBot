#!/usr/bin/env python3
# webhook_logger.py - Simple Telegram bot webhook tester
# Sends commands to webhook and shows the response

import os
import sys
import json
import time
import requests
import argparse
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

def create_session():
    """Create a requests session with retries"""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def create_update(chat_id, text):
    """Create a simulated Telegram update object for the command"""
    current_time = int(time.time())
    
    # Create default entities for bot commands
    entities = None
    if text.startswith('/'):
        command_length = text.find(' ') if ' ' in text else len(text)
        entities = [{
            "offset": 0,
            "length": command_length,
            "type": "bot_command"
        }]
        
    # Build the update object
    update = {
        "update_id": 10000,
        "message": {
            "message_id": 1,
            "from": {
                "id": chat_id,
                "first_name": "Test",
                "username": "test_user"
            },
            "chat": {
                "id": chat_id,
                "first_name": "Test",
                "username": "test_user",
                "type": "private"
            },
            "date": current_time,
            "text": text
        }
    }
    
    # Add entities if needed
    if entities:
        update["message"]["entities"] = entities
        
    return update

def create_callback_query(chat_id, callback_data):
    """Create a simulated callback query update"""
    current_time = int(time.time())
    
    # Build the callback query update
    update = {
        "update_id": 10001,
        "callback_query": {
            "id": f"10001_{current_time}",
            "from": {
                "id": chat_id,
                "first_name": "Test",
                "username": "test_user"
            },
            "message": {
                "message_id": 2,
                "from": {
                    "id": chat_id,
                    "first_name": "Test Bot",
                    "username": "test_bot",
                    "is_bot": True
                },
                "chat": {
                    "id": chat_id,
                    "first_name": "Test",
                    "username": "test_user",
                    "type": "private"
                },
                "date": current_time - 10,
                "text": "Test message with buttons"
            },
            "chat_instance": f"{chat_id}_{current_time}",
            "data": callback_data
        }
    }
    
    return update

def notify_telegram(chat_id, message, token):
    """Send a notification message to Telegram"""
    if not token:
        return False
        
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        session = create_session()
        response = session.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            print_color("✓ Notification sent to Telegram", Colors.GREEN)
            return True
        else:
            print_color(f"✗ Failed to send notification: {response.status_code}", Colors.RED)
            return False
    except Exception as e:
        print_color(f"✗ Error sending notification: {str(e)}", Colors.RED)
        return False

def test_webhook(url, chat_id, command, token=None, callback=False, verbose=False, show_webhook_info=False):
    """Send command to webhook and show the response"""
    try:
        # Create update based on type
        if callback:
            update = create_callback_query(chat_id, command)
            print_color(f"CALLBACK QUERY: {command}", Colors.BLUE)
        else:
            update = create_update(chat_id, command)
            print_color(f"COMMAND: {command}", Colors.BLUE)
        
        if verbose:
            print_color("REQUEST:", Colors.YELLOW)
            print(json.dumps(update, indent=2))
        
        # Send the request with retries
        print_color(f"Sending to webhook: {url}", Colors.YELLOW)
        start_time = time.time()
        
        session = create_session()
        response = session.post(
            url,
            json=update,
            headers={"Content-Type": "application/json"},
            timeout=(5, 30)  # (connect timeout, read timeout)
        )
        response_time = time.time() - start_time
        
        # Show the response status
        if 200 <= response.status_code < 300:
            status_text = f"✓ Webhook responded: {response.status_code} ({response_time:.2f}s)"
            print_color(status_text, Colors.GREEN)
            success = True
        else:
            status_text = f"✗ Webhook error: {response.status_code}"
            print_color(status_text, Colors.RED)
            success = False
        
        if verbose and response.text:
            print_color("\nWebhook Response Content:", Colors.YELLOW)
            try:
                # Try to format as JSON if possible
                response_json = response.json()
                print(json.dumps(response_json, indent=2))
            except:
                print(response.text)
        
        # Send a confirmation message via Telegram API if token is provided
        if token:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"<b>Webhook Test</b>\n"
            message += f"<b>Time:</b> {timestamp}\n"
            message += f"<b>Command:</b> {command}\n"
            message += f"<b>Status:</b> {'✅ Success' if success else '❌ Failed'}\n"
            message += f"<b>Response Time:</b> {response_time:.2f}s"
            
            notify_telegram(chat_id, message, token)
            
        return success
            
    except requests.exceptions.Timeout:
        print_color(f"ERROR: Request timed out after {time.time() - start_time:.1f}s", Colors.RED)
        print_color("Try increasing the timeout with --timeout option", Colors.YELLOW)
        return False
    except requests.exceptions.ConnectionError:
        print_color(f"ERROR: Could not connect to {url}", Colors.RED)
        return False
    except Exception as e:
        print_color(f"ERROR: {str(e)}", Colors.RED)
        return False

def main():
    """Parse arguments and run the test"""
    parser = argparse.ArgumentParser(description="Test Telegram bot webhooks")
    parser.add_argument("url", help="The webhook URL to test")
    parser.add_argument("chat_id", type=int, help="The chat ID to use for testing")
    parser.add_argument("command", help="The command or callback data to send")
    parser.add_argument("--callback", action="store_true", help="Send a callback query instead of a message")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    parser.add_argument("--token", help="Bot token for sending confirmation via Telegram API")
    
    args = parser.parse_args()
    
    # Run the test
    success = test_webhook(
        args.url,
        args.chat_id,
        args.command,
        token=args.token,
        callback=args.callback,
        verbose=args.verbose
    )
    
    # Set exit code based on success
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()