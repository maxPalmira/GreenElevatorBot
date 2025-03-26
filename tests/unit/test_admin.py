import os
import tempfile
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, Chat, User, CallbackQuery
from src.utils.db.init_db import init_test_db
from src.loader import dp, db
from src.handlers.menu import admin_menu_handler
from src.handlers.admin.products import process_products
from src.handlers.admin.orders import process_orders
from src.handlers.admin.questions import process_questions
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from src.filters.is_admin import IsAdmin

# Set up memory storage for state management
dp.storage = MemoryStorage()

@pytest.fixture
async def test_db():
    """Create temporary test database"""
    # Create temp file
    db_fd, db_path = tempfile.mkstemp()
    print(f"\nTest database path: {db_path}")
    
    # Update app database path
    db.db_path = db_path
    
    # Initialize test database with schema and test data
    test_db = init_test_db(db_path)
    
    # Verify schema
    schema = test_db.query("SELECT sql FROM sqlite_master WHERE type='table' AND name='products'", fetchone=True)
    print(f"\nProducts table schema: {schema[0] if schema else 'Not found!'}")
    
    yield test_db
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
async def admin_message_mock():
    """Create a mock message for admin tests"""
    message = AsyncMock(spec=Message)
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 12345
    message.from_user.username = "admin"
    message.chat = MagicMock(spec=Chat)
    message.chat.id = 12345
    message.text = ""
    return message

@pytest.fixture
async def admin_callback_mock():
    """Create a mock callback query for admin tests"""
    query = AsyncMock(spec=CallbackQuery)
    query.from_user = MagicMock(spec=User)
    query.from_user.id = 12345
    query.from_user.username = "admin"
    query.message = AsyncMock(spec=Message)
    query.message.chat = MagicMock(spec=Chat)
    query.message.chat.id = 12345
    return query

@pytest.fixture
async def state_mock():
    """Mock FSM state"""
    state = MagicMock(spec=FSMContext)
    state.get_state = AsyncMock(return_value=None)
    state.set_state = AsyncMock()
    state.finish = AsyncMock()
    return state

class TestAdminHandlers:
    """Test suite for admin handlers"""
    
    @pytest.mark.asyncio
    @patch('src.filters.is_admin.ADMINS', [12345])  # Mock ADMINS list to include test user ID
    @patch('src.handlers.menu.db')  # Mock the database in the menu handler
    async def test_admin_menu(self, db_mock, admin_message_mock, test_db):
        """Test admin menu command"""
        print("\n==================== Testing admin menu ====================")
        
        # Set command
        message = await admin_message_mock
        message.text = '/menu'
        
        # Create filter with test database
        admin_filter = IsAdmin()
        
        # Check if user has admin access
        is_admin = await admin_filter.check(message)
        assert is_admin, "User should have admin access"
        
        # Handle command
        await admin_menu_handler(message)
        
        # Verify response
        message.answer.assert_called_once()
        assert "Admin Menu" in message.answer.call_args[0][0]
    
    async def test_products_management(self, admin_callback_mock, test_db):
        """Test products management"""
        print("\n==================== Testing products management ====================")
        
        # Handle callback
        await process_products(admin_callback_mock.message)
        
        # Verify response
        assert admin_callback_mock.message.answer.call_count + admin_callback_mock.message.answer_photo.call_count > 0
        
        # Check if product info is in any response
        found = False
        for call in admin_callback_mock.message.answer.call_args_list + admin_callback_mock.message.answer_photo.call_args_list:
            text = call[1].get('caption', '') or call[0][0]
            print(f"\nResponse text: {text}")
            if 'Test Product' in text and '$990.00' in text and '🔥 Premium Strains' in text:
                found = True
                break
        assert found, "Product information not found in responses"
    
    async def test_orders_view(self, admin_callback_mock, test_db):
        """Test orders view"""
        print("\n==================== Testing orders view ====================")
        
        # Handle callback
        await process_orders(admin_callback_mock.message)
        
        # Verify response
        admin_callback_mock.message.answer.assert_called()
        
        # Check if order info is in any response
        found = False
        for call in admin_callback_mock.message.answer.call_args_list:
            text = call[0][0]
            if 'Test Product' in text and 'pending' in text:
                found = True
                break
        assert found, "Order information not found in responses"
    
    async def test_questions_view(self, admin_callback_mock, test_db):
        """Test questions view"""
        print("\n==================== Testing questions view ====================")
        
        # Handle callback
        await process_questions(admin_callback_mock.message)
        
        # Verify response
        admin_callback_mock.message.answer.assert_called()
        
        # Check if question info is in any response
        found = False
        for call in admin_callback_mock.message.answer.call_args_list:
            text = call[0][0]
            if 'Test question?' in text and 'pending' in text:
                found = True
                break
        assert found, "Question information not found in responses"
    
    @pytest.mark.asyncio
    @patch('src.filters.is_admin.ADMINS', [])  # Mock ADMINS list to be empty
    @patch('src.handlers.menu.db')  # Mock the database in the menu handler
    async def test_unauthorized_access(self, db_mock, admin_message_mock, test_db):
        """Test unauthorized access to admin menu"""
        print("\n==================== Testing unauthorized access ====================")
        
        # Update user role to non-admin
        message = await admin_message_mock
        test_db.query('UPDATE users SET role = ? WHERE user_id = ?', ('user', message.from_user.id))
        
        # Create filter with test database
        admin_filter = IsAdmin()
        
        # Check if user has admin access
        is_admin = await admin_filter.check(message)
        assert not is_admin, "User should not have admin access"
        
        # No need to call handler since filter should prevent access
        message.answer.assert_not_called()  # Should not show menu to non-admin users 