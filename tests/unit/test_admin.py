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
from src.handlers.admin import admin_menu, products_management, orders_view, questions_view
from src.config import ADMINS

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

@pytest.fixture
def admin_message():
    message = AsyncMock()
    message.from_user.id = ADMINS[0]  # Use first admin ID from config
    message.from_user.username = "admin"
    return message

@pytest.fixture
def user_message():
    message = AsyncMock()
    message.from_user.id = 123456789  # Non-admin ID
    message.from_user.username = "user"
    return message

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
    
    @pytest.mark.asyncio
    async def test_products_management(self, admin_message):
        """Test products management access by admin"""
        with patch('src.handlers.admin.products.db') as mock_db:
            mock_db.execute.return_value = []  # No products
            await products_management(admin_message)
            admin_message.answer.assert_called_once()
            assert "Products Management" in admin_message.answer.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_orders_view(self, admin_message):
        """Test orders view access by admin"""
        with patch('src.handlers.admin.orders.db') as mock_db:
            mock_db.execute.return_value = []  # No orders
            await orders_view(admin_message)
            admin_message.answer.assert_called_once()
            assert "No orders" in admin_message.answer.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_questions_view(self, admin_message):
        """Test questions view access by admin"""
        with patch('src.handlers.admin.questions.db') as mock_db:
            mock_db.execute.return_value = []  # No questions
            await questions_view(admin_message)
            admin_message.answer.assert_called_once()
            assert "No questions" in admin_message.answer.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, user_message):
        """Test unauthorized access to admin functions"""
        # Test admin menu
        await admin_menu(user_message)
        user_message.answer.assert_called_once()
        assert "unauthorized" in user_message.answer.call_args[0][0].lower()

        # Reset mock
        user_message.reset_mock()

        # Test products management
        await products_management(user_message)
        user_message.answer.assert_called_once()
        assert "unauthorized" in user_message.answer.call_args[0][0].lower()

        # Reset mock
        user_message.reset_mock()

        # Test orders view
        await orders_view(user_message)
        user_message.answer.assert_called_once()
        assert "unauthorized" in user_message.answer.call_args[0][0].lower()

        # Reset mock
        user_message.reset_mock()

        # Test questions view
        await questions_view(user_message)
        user_message.answer.assert_called_once()
        assert "unauthorized" in user_message.answer.call_args[0][0].lower() 