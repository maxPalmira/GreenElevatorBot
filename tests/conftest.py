import pytest
import asyncio
from aiogram import types
from unittest.mock import AsyncMock, patch, MagicMock
from src.loader import dp, db
from tests.config import TEST_ADMIN_IDS, cleanup_test_db
import logging

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
    
    yield  # Run test
    
    # Cleanup
    cleanup_test_db()

@pytest.fixture
def user_mock():
    """Create a mock user for testing"""
    return types.User(
        id=TEST_ADMIN_IDS[0],  # Use test admin ID
        is_bot=False,
        first_name="Test",
        username="test_user",
        language_code="en"
    )

@pytest.fixture
def chat_mock(user_mock):
    """Create a mock chat for testing"""
    return types.Chat(
        id=user_mock.id,  # Use same ID as user
        type=types.ChatType.PRIVATE,
        title=None,
        username=user_mock.username
    )

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def message_mock():
    """Create a mock Message object for testing."""
    message = AsyncMock(spec=types.Message)
    message.from_user = MagicMock(spec=types.User)
    message.from_user.id = 12345
    message.from_user.username = "test_user"
    message.text = "/start"
    message.answer = AsyncMock()
    return message

@pytest.fixture
def bot_mock():
    """Create a mock bot object"""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    bot.send_photo = AsyncMock()
    return bot

@pytest.fixture
def db_mock():
    """Create a mock database object"""
    db = MagicMock()
    db.query = AsyncMock()
    db.execute = AsyncMock()
    return db 