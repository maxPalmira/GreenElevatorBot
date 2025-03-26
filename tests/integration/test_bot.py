import pytest
import logging
import time
import json
import requests
from pathlib import Path
import sys
from aiogram import types, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tests.utils.test_utils import compare_responses, print_header, print_info, print_success, print_failure
from tests.utils.test_utils_integration import send_message, validate_response
from unittest.mock import AsyncMock
from src.handlers.menu import cmd_start, user_menu_handler
from src.handlers.user.catalog import process_catalog
from src.handlers.user.contact import process_contact

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BotTester')

# Bot token from Railway
BOT_TOKEN = "7881793630:AAGBPflLxLtK9Ahmu6QbRSXQhli_W6rfXv4"

@pytest.fixture
async def bot():
    """Bot fixture for testing

Changes:
- 2025-03-23: Fixed import paths"""
    bot = Bot(token=BOT_TOKEN)
    yield bot
    await bot.close()

@pytest.fixture
async def dp():
    """Dispatcher fixture for testing"""
    storage = MemoryStorage()
    dp = Dispatcher(Bot(token=BOT_TOKEN), storage=storage)
    return dp

@pytest.fixture
def message_mock():
    """Create a mock message for testing"""
    message = types.Message()
    message.from_user = types.User(id=238038462, is_bot=False, first_name="Test", username="test_user")
    message.chat = types.Chat(id=238038462, type="private")
    message.text = ""
    message.answer = AsyncMock()
    return message

@pytest.mark.asyncio
class TestBot:
    @pytest.mark.asyncio
    async def test_start_command(self, message_mock):
        """Test the start command"""
        print_header("Testing /start command")

        try:
            # Set command
            message_mock.text = "/start"

            # Call handler
            await cmd_start(message_mock)

            # Define expected content
            expected_content = {
                "text": "Welcome to Green Elevator Wholesale!\n\nPlease select your role:",
                "buttons": [["Customer", "Admin"]]
            }

            # Get actual response
            response_text = message_mock.answer.call_args[0][0]
            response_markup = message_mock.answer.call_args[1].get('reply_markup')

            # Compare and report
            result = compare_responses(expected_content, response_text, response_markup)
            assert result.success, str(result)

        except Exception as e:
            print(f"\n✗ Start command test failed: {str(e)}")
            raise

    @pytest.mark.asyncio
    async def test_menu_command(self, message_mock):
        """Test the menu command"""
        print_header("Testing /menu command")

        try:
            # Set command
            message_mock.text = "/menu"

            # Call handler
            await user_menu_handler(message_mock)

            # Define expected content
            expected_content = {
                "text": "Welcome to Green Elevator Wholesale!\n\nPlease select an option:",
                "buttons": [["🌿 Products"], ["☎️ Contact"]]
            }

            # Get actual response
            response_text = message_mock.answer.call_args[0][0]
            response_markup = message_mock.answer.call_args[1].get('reply_markup')

            # Compare and report
            result = compare_responses(expected_content, response_text, response_markup)
            assert result.success, str(result)

        except Exception as e:
            print(f"\n✗ Menu command test failed: {str(e)}")
            raise

    @pytest.mark.asyncio
    async def test_products_command(self, message_mock):
        """Test the products command"""
        print_header("Testing products command")

        try:
            # Set command
            message_mock.text = "🌿 Products"

            # Call handler
            await process_catalog(message_mock)

            # Define expected content
            expected_content = {
                "text": "Available Products:",
                "buttons": [["🛒 Cart"], ["🔙 Back"]]
            }

            # Get actual response
            response_text = message_mock.answer.call_args[0][0]
            response_markup = message_mock.answer.call_args[1].get('reply_markup')

            # Compare and report
            result = compare_responses(expected_content, response_text, response_markup)
            assert result.success, str(result)

        except Exception as e:
            print(f"\n✗ Products command test failed: {str(e)}")
            raise

    async def test_contact_command(self, message_mock):
        """Test the contact command"""
        print_header("Testing contact command")
        
        try:
            # Set command
            message_mock.text = "☎️ Contact"
            
            # Call handler
            await process_contact(message_mock)
            
            # Define expected content
            expected_content = {
                "prompt": "Please enter your question",
                "info": "team will get back to you"
            }
            
            # Get actual response
            response_text = message_mock.answer.call_args[0][0]
            response_markup = message_mock.answer.call_args[1].get('reply_markup')
            
            # Compare and report
            result = compare_responses(expected_content, response_text, response_markup)
            assert result.success, str(result)
            print_success("Contact command test passed")
            
        except Exception as e:
            print_failure(f"Contact command test failed: {str(e)}")
            raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 