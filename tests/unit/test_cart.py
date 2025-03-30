"""
Description: Unit tests for the cart functionality of the GreenElevator Telegram Bot.
Changes:
1. Initial test implementation for cart command handlers
2. Added structured logging matching test_core.py format
3. Fixed class decorator - removed @pytest.mark.asyncio from class level
4. Fixed import for CheckoutState - corrected the import path
5. Updated to use new database interface (execute instead of query/fetchall)
6. Fixed mock setup for async tests
7. Updated database mock setup to match new interface
8. Fixed async mock setup
9. Updated test expectations
10. Fixed database mock setup
11. Added proper error handling
12. Fixed state management mocks
13. Updated test methods to match actual implementation
14. Fixed message format expectations
15. Added proper callback data structure
16. Fixed callback query message mock
17. Fixed state machine setup for checkout
18. Fixed test_checkout_process to correctly mock state.set method
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock, call
import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, Chat, User

# Import the handlers and states
from src.handlers.user.cart import process_cart, process_add_to_cart, process_remove_from_cart, process_checkout, cart_button, process_shipping_address
from tests.utils.test_utils import print_header, print_info, print_success, print_failure
from src.states.checkout_state import CheckoutState

@pytest.fixture
def message():
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock()
    message.from_user.id = 123456789
    message.from_user.username = "testuser"
    return message

@pytest.fixture
def callback_query():
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = AsyncMock()
    callback.from_user.id = 123456789
    callback.from_user.username = "testuser"
    callback.message = AsyncMock(spec=Message)
    callback.message.from_user = callback.from_user
    return callback

@pytest.fixture
def state():
    state = AsyncMock(spec=FSMContext)
    state.get_data = AsyncMock(return_value={})
    state.set_data = AsyncMock()
    state.update_data = AsyncMock()
    state.finish = AsyncMock()
    state.get_state = AsyncMock(return_value=None)
    state.set_state = AsyncMock()
    return state

class TestCartHandlers:
    """Test cart command handlers"""
    
    @pytest.mark.asyncio
    async def test_process_cart_with_items(self, message):
        """Test processing cart with items"""
        cart_items = [
            (1, "Test Product", 1000, 2)  # idx, title, price (in cents), quantity
        ]
        
        with patch('src.handlers.user.cart.db') as mock_db:
            mock_db.execute.return_value = cart_items
            await process_cart(message)
            
            mock_db.execute.assert_called_once()
            message.answer.assert_called_once()
            
            response_text = message.answer.call_args[0][0]
            assert "🛒 Your Cart:" in response_text
            assert "Test Product" in response_text
            assert "Total: $20.00" in response_text
    
    @pytest.mark.asyncio
    async def test_process_cart_empty(self, message):
        """Test processing empty cart"""
        with patch('src.handlers.user.cart.db') as mock_db:
            mock_db.execute.return_value = []
            await process_cart(message)
            
            mock_db.execute.assert_called_once()
            message.answer.assert_called_once_with('Your cart is empty.')
    
    @pytest.mark.asyncio
    async def test_add_to_cart_new_item(self, callback_query):
        """Test adding new item to cart"""
        product = (1, "Test Product", "Description", "image.jpg", 1000, "tag")
        callback_data = {'action': 'add_to_cart', 'id': '1'}
        
        with patch('src.handlers.user.cart.db') as mock_db:
            mock_db.execute.side_effect = [product, None, None]
            await process_add_to_cart(callback_query, callback_data)
            
            assert mock_db.execute.call_count == 3
            callback_query.answer.assert_called_once_with('Added to cart!')
    
    @pytest.mark.asyncio
    async def test_add_to_cart_existing_item(self, callback_query):
        """Test adding existing item to cart"""
        product = (1, "Test Product", "Description", "image.jpg", 1000, "tag")
        cart_item = (1,)  # quantity
        callback_data = {'action': 'add_to_cart', 'id': '1'}
        
        with patch('src.handlers.user.cart.db') as mock_db:
            mock_db.execute.side_effect = [product, cart_item, None]
            await process_add_to_cart(callback_query, callback_data)
            
            assert mock_db.execute.call_count == 3
            callback_query.answer.assert_called_once_with('Added to cart!')
    
    @pytest.mark.asyncio
    async def test_remove_from_cart(self, callback_query):
        """Test removing item from cart"""
        callback_data = {'action': 'remove_from_cart', 'id': '1'}
        
        with patch('src.handlers.user.cart.db') as mock_db, \
             patch('src.handlers.user.cart.process_cart') as mock_process_cart:
            mock_db.execute.return_value = None
            await process_remove_from_cart(callback_query, callback_data)
            
            mock_db.execute.assert_called_once()
            callback_query.answer.assert_called_once_with('Removed from cart!')
            mock_process_cart.assert_called_once_with(callback_query.message)
    
    @pytest.mark.asyncio
    async def test_checkout_process(self, message, state):
        """Test successful checkout process"""
        cart_items = [
            (1, "Test Product", 1000, 2)  # idx, title, price (in cents), quantity
        ]
        
        with patch('src.handlers.user.cart.db') as mock_db, \
             patch('src.handlers.user.cart.CheckoutState.shipping_address') as mock_shipping_address:
            mock_db.execute.return_value = cart_items
            # Mock the state properly
            mock_shipping_address.set = AsyncMock()
            await process_checkout(message, state)
            
            mock_db.execute.assert_called_once()
            message.answer.assert_called_once()
            assert "Please enter your shipping address:" in message.answer.call_args[0][0]
            assert isinstance(message.answer.call_args[1]['reply_markup'], ReplyKeyboardMarkup)
            state.update_data.assert_called_once_with(cart_items=cart_items, total=2000)
    
    @pytest.mark.asyncio
    async def test_checkout_empty_cart(self, message, state):
        """Test checkout with empty cart"""
        with patch('src.handlers.user.cart.db') as mock_db:
            mock_db.execute.return_value = []
            await process_checkout(message, state)
            
            mock_db.execute.assert_called_once()
            message.answer.assert_called_once_with('Your cart is empty.') 