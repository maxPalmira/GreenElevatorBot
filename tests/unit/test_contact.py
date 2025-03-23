"""
Created: 2023-10-21
Last Updated: 2023-10-21
Description: Unit tests for the contact functionality of the GreenElevator Telegram Bot.
Changes:
- 2023-10-21: Initial test implementation for contact command handlers
- 2023-10-21: Added structured logging in the same format as test_core.py
- 2023-10-21: Fixed coroutine handling in mocks
- 2023-10-21: Added mocks for dispatcher FSM state
- 2023-10-21: Updated tests to match simplified contact handler that displays static information
- 2023-10-21: Updated to use centralized text constant from src.utils.texts
- 2025-03-23: Fixed import paths
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock, call
import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from src.handlers.user.contact import process_contact, process_question, ContactState
from tests.utils.test_utils import print_header, print_info, print_success, print_failure
from tests.config import TEST_ADMIN_IDS
from src.utils.texts import CONTACT_INFO_MESSAGE

def format_keyboard(keyboard, label="Keyboard"):
    """Format keyboard structure for consistent output"""
    formatted = ""
    for i, row in enumerate(keyboard):
        formatted += f"  Row {i+1}: {row}\n"
    return formatted

def print_section(title):
    """Print a section divider with title"""
    # Skip TEXT RESPONSE and BUTTONS headers
    if title in ["TEXT RESPONSE", "BUTTONS"]:
        return
    print(f"\n\n{'=' * 30}\n{title}\n{'=' * 30}\n\n")

@pytest.mark.asyncio
class TestContactHandlers:
    """Test contact command handlers"""
    
    @pytest.mark.asyncio
    async def test_contact_command_displays_info(self, message_mock):
        """Test the contact command handler displays contact information"""
        print_header("Testing /contact command - Displays contact info")
        
        # Execute
        print_info("User requested contact form")
        await process_contact(message_mock)
        
        # Test response text
        print_section("TEXT RESPONSE")
        response_text = message_mock.answer.call_args[0][0]
        print(f"▶ EXPECTED TEXT:\n{CONTACT_INFO_MESSAGE}")
        print(f"▶ ACTUAL TEXT:\n{response_text}")
        
        assert response_text == CONTACT_INFO_MESSAGE
        print_success("All assertions passed - test successful")
    
    @pytest.mark.asyncio
    async def test_process_question_ends_state(self):
        """Test that process_question just ends the state without doing anything else"""
        print_header("Testing question submission - State ends")
        
        # Setup mocks
        message_mock = AsyncMock(spec=types.Message)
        message_mock.text = "This is a test question"
        message_mock.from_user = MagicMock()
        message_mock.from_user.id = 12345
        message_mock.from_user.username = "test_user"
        
        state_mock = AsyncMock(spec=FSMContext)
        
        # Execute
        print_info("User submitted a question (state should be ended)")
        await process_question(message_mock, state_mock)
        
        # Verify state was finished
        state_mock.finish.assert_called_once()
        print_success("All assertions passed - test successful") 