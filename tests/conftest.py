"""
Test configuration and fixtures.
Last Updated: 2024-03-20
Changes:
- Fixed async mock setup
- Added proper message mock configuration
- Added missing attributes to mocks
- Fixed coroutine handling in mocks
- Updated database mock for synchronous operations
- Fixed mock return values for async operations
- Fixed state management mocks
- Fixed message mock to properly handle async methods
- Fixed async fixture setup
"""

import pytest
import asyncio
from aiogram import types
from unittest.mock import AsyncMock, patch, MagicMock, create_autospec
from src.loader import dp, db
from tests.config import TEST_ADMIN_IDS, cleanup_test_db, setup_test_db
import logging
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, Chat, User, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton

# Configure clean logging for tests
logging.basicConfig(level=logging.ERROR)

# Suppress all third-party library logs
for logger_name in ['aiogram', 'sqlalchemy', 'asyncio', 'urllib3', 'pytest', 'PIL']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

# Suppress SQL query logs
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """Setup before and cleanup after each test"""
    # Setup
    cleanup_test_db()  # Ensure clean state
    setup_test_db()  # Initialize test database
    
    yield  # Run test
    
    # Cleanup
    cleanup_test_db()

@pytest.fixture
def user_mock():
    """Create a mock user for testing"""
    user = MagicMock(spec=User)
    user.id = TEST_ADMIN_IDS[0]  # Use test admin ID
    user.is_bot = False
    user.first_name = "Test"
    user.username = "test_user"
    user.language_code = "en"
    return user

@pytest.fixture
def chat_mock(user_mock):
    """Create a mock chat for testing"""
    chat = MagicMock(spec=Chat)
    chat.id = user_mock.id  # Use same ID as user
    chat.type = types.ChatType.PRIVATE
    chat.title = None
    chat.username = user_mock.username
    return chat

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def message_mock(user_mock, chat_mock):
    """Create a mock Message object for testing."""
    message = AsyncMock(spec=Message)
    message.from_user = user_mock
    message.chat = chat_mock
    message.text = "/start"
    message.message_id = 1
    message.date = None
    
    # Mock async methods
    async def mock_answer(*args, **kwargs):
        answer_message = AsyncMock(spec=Message)
        answer_message.message_id = 2
        return answer_message
    
    async def mock_reply(*args, **kwargs):
        reply_message = AsyncMock(spec=Message)
        reply_message.message_id = 3
        return reply_message
    
    message.answer = AsyncMock(side_effect=mock_answer)
    message.reply = AsyncMock(side_effect=mock_reply)
    message.edit_text = AsyncMock()
    message.edit_reply_markup = AsyncMock()
    message.delete = AsyncMock()
    
    return message

@pytest.fixture
def callback_query_mock(message_mock, user_mock):
    """Create a mock CallbackQuery object for testing."""
    query = AsyncMock(spec=CallbackQuery)
    query.from_user = user_mock
    query.message = message_mock
    query.data = "test_data"
    query.id = "test_query_id"
    
    # Mock async methods
    async def mock_answer(*args, **kwargs):
        return None
    
    query.answer = AsyncMock(side_effect=mock_answer)
    query.message.edit_text = AsyncMock()
    query.message.edit_reply_markup = AsyncMock()
    
    return query

@pytest.fixture
def bot_mock():
    """Create a mock bot object"""
    bot = AsyncMock()
    bot.send_message = AsyncMock()
    bot.send_photo = AsyncMock()
    bot.edit_message_text = AsyncMock()
    bot.edit_message_reply_markup = AsyncMock()
    bot.delete_message = AsyncMock()
    bot.send_chat_action = AsyncMock()
    
    # Mock return values
    message = AsyncMock(spec=types.Message)
    message.message_id = 4
    bot.send_message.return_value = message
    bot.send_photo.return_value = message
    
    return bot

@pytest.fixture
def db_mock():
    """Create a mock database object"""
    mock_db = MagicMock()
    
    # Mock execute method for synchronous operations
    def mock_execute(*args, **kwargs):
        if len(args) < 2:
            return None
        
        sql = args[0].lower()
        
        # Handle fetchone and fetchall
        if kwargs.get('fetchone', False):
            if 'select' in sql:
                if 'from cart' in sql:
                    return (1,)  # Return quantity for cart items
                if 'from products' in sql:
                    return ('prod1', 'Test Product 1', 'Description', 'image.jpg', 1000, 'cat1', 12345)
            return None
            
        if kwargs.get('fetchall', False):
            if 'select' in sql:
                if 'from cart' in sql:
                    return [('prod1', 'Test Product 1', 1000, 2), ('prod2', 'Test Product 2', 2000, 1)]
            return []
        
        # Handle commit
        if kwargs.get('commit', False):
            return None
        
        return None
    
    mock_db.execute = MagicMock(side_effect=mock_execute)
    mock_db.get_user_role = MagicMock(return_value="user")
    mock_db.set_user_role = MagicMock(return_value=True)
    
    return mock_db

@pytest.fixture
def state_mock():
    """Create a mock FSMContext object for testing."""
    state = AsyncMock(spec=FSMContext)
    
    # Mock state data
    state_data = {}
    current_state = None
    
    async def mock_set_state(new_state):
        nonlocal current_state
        current_state = new_state
        return None
        
    async def mock_finish():
        nonlocal current_state
        current_state = None
        state_data.clear()
        return None
        
    async def mock_update_data(**kwargs):
        state_data.update(kwargs)
        return None
        
    async def mock_get_data():
        return state_data.copy()
        
    async def mock_get_state():
        return current_state
    
    state.set_state = AsyncMock(side_effect=mock_set_state)
    state.finish = AsyncMock(side_effect=mock_finish)
    state.update_data = AsyncMock(side_effect=mock_update_data)
    state.get_data = AsyncMock(side_effect=mock_get_data)
    state.get_state = AsyncMock(side_effect=mock_get_state)
    
    return state

@pytest.fixture
def dispatcher_mock():
    """Create a mock dispatcher"""
    dp = AsyncMock(spec=Dispatcher)
    dp.current_state.return_value = AsyncMock(spec=FSMContext)
    return dp