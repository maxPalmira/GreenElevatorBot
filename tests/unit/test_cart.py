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
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock, call
import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, Chat, User

# Import the handlers and states
from src.handlers.user.cart import process_cart, process_add_to_cart, process_remove_from_cart, process_checkout, cart_button
from tests.utils.test_utils import print_header, print_info, print_success, print_failure

# Correct import for CheckoutState
from src.states.checkout_state import CheckoutState

def format_keyboard(keyboard, label="Keyboard"):
    """Format keyboard structure for consistent output"""
    formatted = ""
    for i, row in enumerate(keyboard):
        formatted += f"  Row {i+1}: {row}\n"
    return formatted

def print_section(text: str):
    """Print a section divider with text"""
    # Skip TEXT RESPONSE and BUTTONS headers
    if text in ["TEXT RESPONSE", "BUTTONS"]:
        return
    print(f"\n{'=' * 30} {text} {'=' * 30}\n")

class TestCartHandlers:
    """Test cart command handlers"""
    
    @pytest.mark.asyncio
    async def test_process_cart_with_items(self, message_mock, db_mock):
        """Test the cart command handler with items in cart"""
        print_header("Testing /cart command - With items")
        
        # Mock data
        cart_items = [
            ('prod1', 'Test Product 1', 1000, 2),  # id, title, price, quantity
            ('prod2', 'Test Product 2', 2000, 1)
        ]
        
        with patch('src.handlers.user.cart.db', db_mock):
            # Configure mock database response
            db_mock.execute.return_value = cart_items
            
            # Execute
            print_info("User requested cart contents")
            await process_cart(message_mock)
            
            # Verify database query
            print_info("Verifying database was queried correctly")
            db_mock.execute.assert_called_once()
            
            # Test response text
            print_section("TEXT RESPONSE")
            response_text = message_mock.answer.call_args[0][0]
            assert "🛒 Your Cart:" in response_text
            assert "Test Product 1" in response_text
            assert "Test Product 2" in response_text
            assert "Total: $40.00" in response_text
    
    @pytest.mark.asyncio
    async def test_process_cart_empty(self, message_mock, db_mock):
        """Test the cart command handler when cart is empty"""
        print_header("Testing /cart command - Empty cart")
        
        # Expected response for empty cart
        expected_text = '🛒 Your cart is empty.'
        
        with patch('src.handlers.user.cart.db', db_mock):
            # Configure mock database response - empty cart
            db_mock.execute.return_value = []
            
            # Execute
            print_info("User requested empty cart contents")
            await process_cart(message_mock)
            
            # Verify database query
            print_info("Verifying database was queried correctly")
            db_mock.execute.assert_called_once()
            
            # Test response text
            print_section("TEXT RESPONSE")
            response_text = message_mock.answer.call_args[0][0]
            print(f"▶ EXPECTED TEXT:\n{expected_text}")
            print(f"▶ ACTUAL TEXT:\n{response_text}")
            
            assert response_text == expected_text, f"Expected '{expected_text}' but got '{response_text}'"
    
    @pytest.mark.asyncio
    async def test_add_to_cart_new_item(self, callback_query_mock, db_mock):
        """Test adding a new item to cart"""
        print_header("Testing add to cart - New item")
        
        callback_data = {'id': 'prod1', 'action': 'add_to_cart'}
        
        with patch('src.handlers.user.cart.db', db_mock):
            # Configure mock database responses
            db_mock.execute.side_effect = [
                ('prod1', 'Test Product 1', 'Description', 'image.jpg', 1000, 'cat1', 12345),  # Product exists
                None,  # Item not in cart yet
                None  # Insert result
            ]
            
            # Execute
            print_info("User adds new product to cart")
            await process_add_to_cart(callback_query_mock, callback_data)
            
            # Verify product check
            print_info("Verifying product existence was checked")
            assert db_mock.execute.call_count >= 1
            
            # Verify cart check
            print_info("Verifying cart was checked for existing item")
            cart_check_call = db_mock.execute.call_args_list[1]
            assert "SELECT quantity FROM cart" in cart_check_call[0][0]
            assert cart_check_call[0][1] == (callback_query_mock.from_user.id, 'prod1')
            
            # Verify insert query
            print_info("Verifying new item was inserted into cart")
            insert_call = db_mock.execute.call_args_list[2]
            assert "INSERT INTO cart" in insert_call[0][0]
            assert insert_call[0][1] == (callback_query_mock.from_user.id, 'prod1')
            
            # Verify response
            print_info("Verifying user received confirmation")
            callback_query_mock.answer.assert_called_once_with('Added to cart!')
            print_success("All assertions passed - test successful")
    
    @pytest.mark.asyncio
    async def test_add_to_cart_existing_item(self, callback_query_mock, db_mock):
        """Test adding an existing item to cart"""
        print_header("Testing add to cart - Existing item")
        
        callback_data = {'id': 'prod1', 'action': 'add_to_cart'}
        
        with patch('src.handlers.user.cart.db', db_mock):
            # Configure mock database responses
            db_mock.execute.side_effect = [
                ('prod1', 'Test Product 1', 'Description', 'image.jpg', 1000, 'cat1', 12345),  # Product exists
                (1,),  # Item already in cart with quantity 1
                None,  # Update quantity
                None   # Get updated cart
            ]
            
            # Execute
            print_info("User adds existing product to cart")
            await process_add_to_cart(callback_query_mock, callback_data)
            
            # Verify database operations
            assert db_mock.execute.call_count == 4
            callback_query_mock.answer.assert_called_once_with('Added to cart!')
    
    @pytest.mark.asyncio
    async def test_remove_from_cart(self, callback_query_mock, db_mock):
        """Test removing an item from cart"""
        print_header("Testing remove from cart")
        
        callback_data = {'id': 'prod1', 'action': 'remove_from_cart'}
        
        with patch('src.handlers.user.cart.db', db_mock):
            # Configure mock database response
            db_mock.execute.side_effect = [
                None,  # Delete item
                []     # Get updated cart
            ]
            
            # Execute
            print_info("User removes product from cart")
            await process_remove_from_cart(callback_query_mock, callback_data)
            
            # Verify delete query was executed
            print_info("Verifying item was deleted from cart")
            assert db_mock.execute.call_count == 2
            callback_query_mock.answer.assert_called_once_with('Removed from cart!')
    
    @pytest.mark.asyncio
    async def test_checkout_process(self, message_mock, db_mock, state_mock):
        """Test the checkout process"""
        print_header("Testing checkout process")
        
        # Setup mock data
        cart_items = [
            ('prod1', 'Test Product 1', 1000, 2),  # id, title, price, quantity
            ('prod2', 'Test Product 2', 2000, 1)
        ]
        
        with patch('src.handlers.user.cart.db', db_mock), \
             patch('aiogram.dispatcher.Dispatcher.get_current') as mock_get_current:
            # Configure mock database response
            db_mock.execute.return_value = cart_items
            
            # Configure dispatcher mock
            mock_dispatcher = MagicMock()
            mock_dispatcher.current_state.return_value = state_mock
            mock_get_current.return_value = mock_dispatcher
            
            # Execute
            print_info("User initiates checkout")
            await process_checkout(message_mock, state_mock)
            
            # Verify state was set
            state_mock.set_state.assert_called_once_with('CheckoutState:shipping_address')
            message_mock.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_checkout_empty_cart(self, message_mock, db_mock, state_mock):
        """Test checkout with empty cart"""
        print_header("Testing checkout - Empty cart")
        
        with patch('src.handlers.user.cart.db', db_mock), \
             patch('aiogram.dispatcher.Dispatcher.get_current') as mock_get_current:
            # Configure mock database response - empty cart
            db_mock.execute.return_value = []
            
            # Configure dispatcher mock
            mock_dispatcher = MagicMock()
            mock_dispatcher.current_state.return_value = state_mock
            mock_get_current.return_value = mock_dispatcher
            
            # Execute
            print_info("User attempts checkout with empty cart")
            await process_checkout(message_mock, state_mock)
            
            # Verify response
            message_mock.answer.assert_called_once_with('🛒 Your cart is empty.')
            
            # Verify state was not changed
            state_mock.set_state.assert_not_called()
            
            print_success("All assertions passed - test successful") 