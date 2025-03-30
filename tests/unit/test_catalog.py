"""
Created: 2023-05-15
Last Updated: 2024-03-26
Description: Unit tests for the catalog functionality of the GreenElevator Telegram Bot.
Changes:
- 2023-10-01: Enhanced test coverage for category callbacks
- 2023-10-20: Updated log format to match structured logging approach used in test_core.py
- 2023-10-21: Fixed assertions and properly awaited coroutines in tests
- 2024-03-20: Fixed async mock setup for message and callback query mocks
- 2024-03-20: Added proper message mock configuration
- 2024-03-20: Fixed coroutine handling in mocks
- 2024-03-26: Updated test expectations to match current catalog implementation
- 2024-03-26: Fixed duplicate test method names
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock, call
import logging
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from src.handlers.user.catalog import process_catalog, category_callback_handler, show_products
from tests.utils.test_utils import print_header, print_info, print_success, print_failure

# Test data matching actual database format
TEST_PRODUCTS = [
    ('thai_premium', 'Premium Thai', 'Our signature Thai strain...', 'https://i.ibb.co/VqFgzVk/product1-1.jpg', 99000, 'Premium Strains'),
    ('island_blend', 'Island Blend', 'A unique blend...', 'https://i.ibb.co/0MdRHKd/product2-1.jpg', 99000, 'Hybrid Strains')
]

TEST_CART_ITEMS = [
    (12345, 'thai_premium', 2),
    (12345, 'island_blend', 1)
]

@pytest.fixture
def mock_db():
    """Mock database connection"""
    mock = MagicMock()
    mock.execute = MagicMock()
    return mock

@pytest.fixture
async def mock_message():
    """Create a mock message"""
    message = AsyncMock(spec=Message)
    message.from_user.id = 12345
    message.chat.id = 12345
    return message

@pytest.fixture
async def mock_callback_query():
    """Create a mock callback query"""
    query = AsyncMock(spec=CallbackQuery)
    query.from_user.id = 12345
    query.message = AsyncMock(spec=Message)
    query.message.chat.id = 12345
    return query

@pytest.fixture
def mock_bot():
    """Mock bot object"""
    bot = AsyncMock()
    bot.send_chat_action = AsyncMock()
    bot.send_photo = AsyncMock()
    return bot

@pytest.fixture
def mock_show_products():
    """Mock show_products function"""
    with patch('src.handlers.user.catalog.show_products') as mock:
        mock.return_value = AsyncMock()
        yield mock

@pytest.fixture
def message():
    message = AsyncMock()
    message.from_user.id = 123456789
    message.from_user.username = "testuser"
    return message

@pytest.fixture
def callback_query():
    callback = AsyncMock()
    callback.from_user.id = 123456789
    callback.from_user.username = "testuser"
    callback.data = "category_1"  # Category ID 1
    return callback

@pytest.mark.asyncio
async def test_process_catalog_with_products_simple(mock_message):
    """Test catalog processing with products"""
    print_header("Testing process_catalog with products")
    
    with patch('src.handlers.user.catalog.show_products', AsyncMock()) as mock_show_products, \
         patch('src.handlers.user.catalog.db') as mock_db, \
         patch('src.handlers.user.catalog.bot') as mock_bot:
        # Setup mock database response
        mock_db.execute.return_value = TEST_PRODUCTS
        mock_bot.send_chat_action = AsyncMock()
        
        # Execute
        print_info("Executing process_catalog function")
        await process_catalog(mock_message)
        
        # Verify database was queried
        mock_db.execute.assert_called()
        
        # Verify show_products was called with correct arguments
        mock_show_products.assert_called_once_with(mock_message, TEST_PRODUCTS)
        
        print_success("Test passed successfully")

@pytest.mark.asyncio
async def test_process_catalog_empty_simple(message):
    """Test catalog processing with no products"""
    with patch('src.handlers.user.catalog.db') as mock_db:
        mock_db.execute.return_value = []
        await process_catalog(message)
        
        # Verify database was queried
        mock_db.execute.assert_called_once()
        # Verify empty catalog message
        message.answer.assert_called_once_with('No products available.')

@pytest.mark.asyncio
async def test_category_callback_handler_simple(mock_callback_query):
    """Test category callback handling with products"""
    print_header("Testing category_callback_handler with products")
    
    callback_data = {'id': '1', 'action': 'view'}
    
    with patch('src.handlers.user.catalog.show_products', AsyncMock()) as mock_show_products, \
         patch('src.handlers.user.catalog.db') as mock_db, \
         patch('src.handlers.user.catalog.bot') as mock_bot:
        mock_db.execute.return_value = TEST_PRODUCTS
        mock_bot.send_chat_action = AsyncMock()
        
        await category_callback_handler(mock_callback_query, callback_data)
        
        # Verify database was queried
        mock_db.execute.assert_called_once()
        # Verify callback was answered
        mock_callback_query.answer.assert_called_once_with('Showing products in category')
        # Verify show_products was called with correct arguments
        mock_show_products.assert_called_once_with(mock_callback_query.message, TEST_PRODUCTS)
        
        print_success("Test passed successfully")

@pytest.mark.asyncio
async def test_category_callback_empty_simple(callback_query):
    """Test category callback handling with no products"""
    callback_data = {'id': '1', 'action': 'view'}
    
    with patch('src.handlers.user.catalog.db') as mock_db:
        mock_db.execute.return_value = []
        await category_callback_handler(callback_query, callback_data)
        
        # Verify database was queried
        mock_db.execute.assert_called_once()
        # Verify callback was answered
        callback_query.answer.assert_called_once_with('No products in this category')

@pytest.mark.asyncio
async def test_process_catalog_detailed(mock_message):
    """Test process_catalog function when no products exist"""
    print_header("Testing process_catalog with no products")
    
    # Setup
    print_info("Setting up test environment with empty product list")
    
    # Mock the show_products function to avoid its internal calls
    with patch('src.handlers.user.catalog.show_products', AsyncMock()) as mock_show_products, \
         patch('src.handlers.user.catalog.db') as mock_db, \
         patch('src.handlers.user.catalog.bot') as mock_bot:
        mock_db.execute.return_value = []
        # Execute
        print_info("Executing process_catalog function")
        await process_catalog(mock_message)
        
        # Verify response
        mock_message.answer.assert_called_once_with('No products available.')
        mock_show_products.assert_not_called()
        
        print_success("Test passed successfully")

@pytest.mark.asyncio
async def test_category_callback_handler_detailed(mock_callback_query):
    """Test category_callback_handler function"""
    print_header("Testing category_callback_handler")
    
    # Setup
    print_info("Setting up test environment")
    callback_data = {"id": "cat1", "action": "view"}
    
    # Mock the show_products function
    with patch('src.handlers.user.catalog.show_products', AsyncMock()) as mock_show_products, \
         patch('src.handlers.user.catalog.db') as mock_db, \
         patch('src.handlers.user.catalog.bot') as mock_bot:
        mock_db.execute.return_value = TEST_PRODUCTS
        # Execute
        print_info("Executing category_callback_handler function")
        await category_callback_handler(mock_callback_query, callback_data)
        
        # Verify response
        mock_callback_query.answer.assert_called_once_with('Showing products in category')
        mock_show_products.assert_called_once_with(mock_callback_query.message, TEST_PRODUCTS)
        
        print_success("Test passed successfully")

@pytest.mark.asyncio
async def test_category_callback_empty_detailed(mock_callback_query):
    """Test category_callback_handler function when no products in category"""
    print_header("Testing category_callback_handler with no products")
    
    # Setup
    print_info("Setting up test environment with empty product list")
    callback_data = {"id": "cat1", "action": "view"}
    
    # Mock the show_products function
    with patch('src.handlers.user.catalog.show_products', AsyncMock()) as mock_show_products, \
         patch('src.handlers.user.catalog.db') as mock_db, \
         patch('src.handlers.user.catalog.bot') as mock_bot:
        mock_db.execute.return_value = []
        # Execute
        print_info("Executing category_callback_handler function")
        await category_callback_handler(mock_callback_query, callback_data)
        
        # Verify response
        mock_callback_query.answer.assert_called_once_with('No products in this category')
        mock_show_products.assert_not_called()
        
        print_success("All assertions passed - test successful") 