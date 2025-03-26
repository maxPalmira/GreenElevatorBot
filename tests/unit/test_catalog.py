"""
Created: 2023-05-15
Last Updated: 2024-03-20
Description: Unit tests for the catalog functionality of the GreenElevator Telegram Bot.
Changes:
- 2023-10-01: Enhanced test coverage for category callbacks
- 2023-10-20: Updated log format to match structured logging approach used in test_core.py
- 2023-10-21: Fixed assertions and properly awaited coroutines in tests
- 2024-03-20: Fixed async mock setup for message and callback query mocks
- 2024-03-20: Added proper message mock configuration
- 2024-03-20: Fixed coroutine handling in mocks
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock, call
import logging
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from src.handlers.user.catalog import process_catalog, category_callback_handler, show_products
from tests.utils.test_utils import print_header, print_info, print_success, print_failure

# Test data
TEST_PRODUCTS = [
    ('prod1', 'Test Product 1', 'Description 1', 'image1.jpg', 1000, 'Category 1'),
    ('prod2', 'Test Product 2', 'Description 2', 'image2.jpg', 2000, 'Category 2')
]

TEST_CART_ITEMS = [
    ('user1', 'prod1', 2),
    ('user1', 'prod2', 1)
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

@pytest.mark.asyncio
async def test_process_catalog_with_products(mock_db, mock_message, mock_bot):
    """Test process_catalog function when products exist"""
    print_header("Testing process_catalog with products")
    
    # Setup
    print_info("Setting up test environment")
    
    # Configure mock_db execute to return the test products
    mock_db.execute.return_value = TEST_PRODUCTS
    
    # Mock the show_products function to avoid its internal calls
    with patch('src.handlers.user.catalog.show_products', AsyncMock()) as mock_show_products:
        # Patch the db and bot in the module
        with patch('src.handlers.user.catalog.db', mock_db), patch('src.handlers.user.catalog.bot', mock_bot):
            # Execute
            print_info("Executing process_catalog function")
            await process_catalog(mock_message)
            
            # Verify
            print_info("Verifying database was queried correctly")
            mock_db.execute.assert_called_once()
            sql_query = mock_db.execute.call_args[0][0]
            kwargs = mock_db.execute.call_args[1]
            
            print_info("Expected SQL: SELECT with JOIN for products and categories")
            print_info(f"Actual SQL: {sql_query}")
            
            assert "SELECT" in sql_query
            assert "products p" in sql_query
            assert "LEFT JOIN categories" in sql_query
            assert kwargs.get('fetchall') is True
            
            # Check that show_products was called
            print_info("Verifying show_products was called with correct arguments")
            mock_show_products.assert_called_once_with(mock_message, TEST_PRODUCTS)
            
            print_success("All assertions passed - test successful")

@pytest.mark.asyncio
async def test_process_catalog_no_products(mock_db, mock_message, mock_bot):
    """Test process_catalog function when no products exist"""
    print_header("Testing process_catalog with no products")
    
    # Setup
    print_info("Setting up test environment with empty product list")
    mock_db.execute.return_value = []
    
    # Mock the show_products function to avoid its internal calls
    with patch('src.handlers.user.catalog.show_products', AsyncMock()) as mock_show_products:
        # Patch the db and bot in the module
        with patch('src.handlers.user.catalog.db', mock_db), patch('src.handlers.user.catalog.bot', mock_bot):
            # Execute
            print_info("Executing process_catalog function")
            await process_catalog(await mock_message)
            
            # Verify response
            mock_message.answer.assert_called_once_with('No products available.')

@pytest.mark.asyncio
async def test_category_callback_handler(mock_db, mock_callback_query, mock_bot):
    """Test category_callback_handler function"""
    print_header("Testing category_callback_handler")
    
    # Setup
    print_info("Setting up test environment")
    callback_data = {"id": "cat1", "action": "view"}
    mock_db.execute.return_value = TEST_PRODUCTS
    
    # Mock the show_products function
    with patch('src.handlers.user.catalog.show_products', AsyncMock()) as mock_show_products:
        # Patch the db and bot in the module
        with patch('src.handlers.user.catalog.db', mock_db), patch('src.handlers.user.catalog.bot', mock_bot):
            # Execute
            print_info("Executing category_callback_handler function")
            query = await mock_callback_query
            await category_callback_handler(query, callback_data)
            
            # Verify response
            query.answer.assert_called_once_with('Showing products in category')
            mock_show_products.assert_called_once()

@pytest.mark.asyncio
async def test_category_callback_handler_no_products(mock_db, mock_callback_query, mock_bot):
    """Test category_callback_handler function when no products in category"""
    print_header("Testing category_callback_handler with no products")
    
    # Setup
    print_info("Setting up test environment with empty product list")
    callback_data = {"id": "cat1", "action": "view"}
    mock_db.execute.return_value = []
    
    # Mock the show_products function
    with patch('src.handlers.user.catalog.show_products', AsyncMock()) as mock_show_products:
        # Patch the db and bot in the module
        with patch('src.handlers.user.catalog.db', mock_db), patch('src.handlers.user.catalog.bot', mock_bot):
            # Execute
            print_info("Executing category_callback_handler function")
            query = await mock_callback_query
            await category_callback_handler(query, callback_data)
            
            # Verify response
            query.answer.assert_called_once_with('No products in this category')
            mock_show_products.assert_not_called()
            
            print_success("All assertions passed - test successful") 