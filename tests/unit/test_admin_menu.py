# Change log: Created dedicated test for admin menu from consolidated menu.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, Chat, User
from src.handlers.menu import admin_menu_handler
from src.utils.texts import ADMIN_MENU_MESSAGE

@pytest.fixture
async def admin_message_mock():
    """Mock admin message"""
    message = MagicMock(spec=Message)
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 12345
    message.from_user.username = "admin"
    message.chat = MagicMock(spec=Chat)
    message.chat.id = 12345
    message.chat.type = "private"
    message.answer = AsyncMock()
    return message

@pytest.mark.asyncio
class TestAdminMenu:
    """Test admin menu handler from consolidated menu.py"""
    
    @pytest.fixture(autouse=True)
    def setup_db_mock(self, db_mock):
        """Setup database mock for each test"""
        with patch('src.handlers.menu.db', db_mock):
            yield
    
    @patch('src.filters.is_admin.ADMINS', [12345])  # Mock ADMINS list to include test user ID
    async def test_admin_menu(self, admin_message_mock):
        """Test admin menu command"""
        print("\nTesting admin menu")  # Simplified format for easier detection
        
        # Get message mock
        message = await admin_message_mock
        
        # Set command
        message.text = '/menu'
        
        # Handle command
        await admin_menu_handler(message)
        
        # Verify response
        message.answer.assert_called_once()
        response_text = message.answer.call_args[0][0]
        assert response_text == ADMIN_MENU_MESSAGE, "Expected admin menu message to match exactly"
        
        # Verify markup was included
        response_markup = message.answer.call_args[1].get('reply_markup')
        assert response_markup is not None, "Expected markup to be present" 