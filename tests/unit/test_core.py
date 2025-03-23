import pytest
from aiogram import types
from src.app import debug_handler
from tests.utils.test_utils import print_header
import traceback
import json
from unittest.mock import AsyncMock

def print_section(title):
    """Print a section divider with title"""
    # Skip TEXT RESPONSE and BUTTONS headers
    if title in ["TEXT RESPONSE", "BUTTONS"]:
        return
    print(f"\n{'=' * 30} {title} {'=' * 30}\n")

@pytest.mark.asyncio
class TestCoreHandlers:
    """Test core bot functionality not tied to specific modules"""
    
    async def test_invalid_command(self, message_mock):
        """Test handling of invalid commands"""
        print("\nTesting invalid command handling")
        
        message_mock.text = "/invalid_command"
        await debug_handler(message_mock)
        
        # Verify response
        message_mock.answer.assert_called_once()
        response_text = message_mock.answer.call_args[0][0]
        
        # Print expected and actual output for verification
        print(f"▶ EXPECTED TEXT:\nSorry, I don't understand that command. Try /start or /menu")
        print(f"▶ ACTUAL TEXT:\n{response_text}")
        assert "Sorry, I don't understand that command" in response_text, "Invalid command message not found"
        
        # Verify no markup was sent
        assert 'reply_markup' not in message_mock.answer.call_args[1], "No markup should be sent for invalid commands" 