"""
Created: 2023-10-21
Last Updated: 2023-10-21
Description: Unit tests for the cart functionality of the GreenElevator Telegram Bot.
Changes:
- 2023-10-21: Initial test implementation for cart command handlers
- 2023-10-21: Added structured logging matching test_core.py format
- 2023-10-21: Fixed class decorator - removed @pytest.mark.asyncio from class level
- 2023-10-21: Fixed import for CheckoutState - corrected the import path
- 2025-03-23: Fixed import for test_utils - updated to use tests.utils instead of src.utils
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock, call
import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup

# Import the handlers and states
from src.handlers.user.cart import process_cart, process_add_to_cart, process_remove_from_cart, process_checkout
from tests.utils.test_utils import print_header, print_info, print_success, print_failure

# Correct import for CheckoutState
from src.states.checkout_state import CheckoutState

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
    print(f"\n{'=' * 30} {title} {'=' * 30}\n")

class TestCartHandlers:
    """Test cart command handlers"""
    
    @pytest.mark.asyncio
    async def test_process_cart_with_items(self, message_mock):
        """Test the cart command handler when cart has items"""
        print_header("Testing /cart command - Cart with items")
        
        # Setup mock data
        cart_items = [
            ('prod1', 'Test Product 1', 1000, 2),  # id, title, price (in cents), quantity
            ('prod2', 'Test Product 2', 2000, 1)
        ]
        
        expected_total = (1000 * 2) + (2000 * 1)  # 2 of prod1 + 1 of prod2
        
        # Expected response - full cart details
        expected_text = '🛒 Your Cart:\n\n'
        expected_text += '🏷 Test Product 1\n📊 Quantity: 2\n💰 Price: $10.00\n💵 Subtotal: $20.00\n─────────────────\n'
        expected_text += '🏷 Test Product 2\n📊 Quantity: 1\n💰 Price: $20.00\n💵 Subtotal: $20.00\n─────────────────\n'
        expected_text += f'\n💳 Total: ${expected_total/100:.2f}'
        
        # Expected buttons
        expected_markup = [
            ['📦 Checkout'],
            ['🔙 Back to Menu']
        ]
        
        with patch('src.handlers.user.cart.db') as mock_db:
            # Configure mock database response
            mock_db.fetchall.return_value = cart_items
            
            # Execute
            print_info("User requested cart contents")
            await process_cart(message_mock)
            
            # Verify database query
            print_info("Verifying database was queried correctly")
            mock_db.fetchall.assert_called_once()
            sql_query = mock_db.fetchall.call_args[0][0]
            params = mock_db.fetchall.call_args[0][1]
            
            print_info("Expected SQL: SELECT joining cart and products")
            print_info(f"Actual SQL: {sql_query}")
            
            assert "SELECT p.idx, p.title, p.price, c.quantity" in sql_query
            assert "FROM cart c" in sql_query
            assert "JOIN products p" in sql_query
            assert "WHERE c.user_id = ?" in sql_query
            assert params == (message_mock.from_user.id,)
            
            # Test response text
            print_section("TEXT RESPONSE")
            response_text = message_mock.answer.call_args[0][0]
            print(f"▶ EXPECTED TEXT:\n{expected_text}")
            print(f"▶ ACTUAL TEXT:\n{response_text}")
            
            assert response_text == expected_text
            
            # Test markup buttons
            print_section("BUTTONS")
            response_markup = message_mock.answer.call_args[1].get('reply_markup')
            
            print(f"▶ EXPECTED BUTTONS:")
            for row in expected_markup:
                print(f"  Row: {row}")
            
            print(f"▶ ACTUAL BUTTONS:")
            for row in response_markup.keyboard:
                button_texts = [btn.text if hasattr(btn, 'text') else btn for btn in row]
                print(f"  Row: {button_texts}")
            
            assert isinstance(response_markup, ReplyKeyboardMarkup)
            assert len(response_markup.keyboard) == 2
            
            # Check first row - Checkout button
            assert len(response_markup.keyboard[0]) == 1
            first_button = response_markup.keyboard[0][0]
            assert (first_button == '📦 Checkout' or 
                    (hasattr(first_button, 'text') and first_button.text == '📦 Checkout'))
            
            # Check second row - Back button
            assert len(response_markup.keyboard[1]) == 1
            second_button = response_markup.keyboard[1][0]
            assert (second_button == '🔙 Back to Menu' or 
                    (hasattr(second_button, 'text') and second_button.text == '🔙 Back to Menu'))
            
            print_success("All assertions passed - test successful")
    
    @pytest.mark.asyncio
    async def test_process_cart_empty(self, message_mock):
        """Test the cart command handler when cart is empty"""
        print_header("Testing /cart command - Empty cart")
        
        # Expected response for empty cart
        expected_text = 'Your cart is empty.'
        
        with patch('src.handlers.user.cart.db') as mock_db:
            # Configure mock database response - empty cart
            mock_db.fetchall.return_value = []
            
            # Execute
            print_info("User requested empty cart contents")
            await process_cart(message_mock)
            
            # Verify database query
            print_info("Verifying database was queried correctly")
            mock_db.fetchall.assert_called_once()
            
            # Test response text
            print_section("TEXT RESPONSE")
            response_text = message_mock.answer.call_args[0][0]
            print(f"▶ EXPECTED TEXT:\n{expected_text}")
            print(f"▶ ACTUAL TEXT:\n{response_text}")
            
            assert response_text == expected_text
            print_success("All assertions passed - test successful")
    
    @pytest.mark.asyncio
    async def test_add_to_cart_new_item(self):
        """Test adding a new item to cart"""
        print_header("Testing add to cart - New item")
        
        # Setup mock
        query_mock = AsyncMock(spec=types.CallbackQuery)
        query_mock.from_user.id = 12345
        callback_data = {'id': 'prod1', 'action': 'add_to_cart'}
        
        with patch('src.handlers.user.cart.db') as mock_db:
            # Configure mock database responses
            mock_db.fetchone.side_effect = [
                ('prod1', 'Test Product 1', 'Description', 'image.jpg', 1000, 'cat1'),  # Product exists
                None  # Item not in cart yet
            ]
            
            # Execute
            print_info("User adds new product to cart")
            await process_add_to_cart(query_mock, callback_data)
            
            # Verify product check
            print_info("Verifying product existence was checked")
            mock_db.fetchone.assert_called()
            
            # Verify cart check
            print_info("Verifying cart was checked for existing item")
            call_args = mock_db.fetchone.call_args_list[1]
            assert "SELECT quantity FROM cart" in call_args[0][0]
            assert call_args[0][1] == (query_mock.from_user.id, 'prod1')
            
            # Verify insert query
            print_info("Verifying new item was inserted into cart")
            mock_db.query.assert_called_once()
            insert_query = mock_db.query.call_args[0][0]
            params = mock_db.query.call_args[0][1]
            
            assert "INSERT INTO cart" in insert_query
            assert params == (query_mock.from_user.id, 'prod1')
            
            # Verify response
            print_info("Verifying user received confirmation")
            query_mock.answer.assert_called_once_with('Added to cart!')
            
            print_success("All assertions passed - test successful")
    
    @pytest.mark.asyncio
    async def test_add_to_cart_existing_item(self):
        """Test adding an existing item to cart (incrementing quantity)"""
        print_header("Testing add to cart - Existing item")
        
        # Setup mock
        query_mock = AsyncMock(spec=types.CallbackQuery)
        query_mock.from_user.id = 12345
        callback_data = {'id': 'prod1', 'action': 'add_to_cart'}
        
        with patch('src.handlers.user.cart.db') as mock_db:
            # Configure mock database responses
            mock_db.fetchone.side_effect = [
                ('prod1', 'Test Product 1', 'Description', 'image.jpg', 1000, 'cat1'),  # Product exists
                (1,)  # Item already in cart with quantity 1
            ]
            
            # Execute
            print_info("User adds existing product to cart")
            await process_add_to_cart(query_mock, callback_data)
            
            # Verify product check
            print_info("Verifying product existence was checked")
            mock_db.fetchone.assert_called()
            
            # Verify cart check
            print_info("Verifying cart was checked for existing item")
            call_args = mock_db.fetchone.call_args_list[1]
            assert "SELECT quantity FROM cart" in call_args[0][0]
            assert call_args[0][1] == (query_mock.from_user.id, 'prod1')
            
            # Verify update query
            print_info("Verifying item quantity was updated")
            mock_db.query.assert_called_once()
            update_query = mock_db.query.call_args[0][0]
            params = mock_db.query.call_args[0][1]
            
            assert "UPDATE cart SET quantity=quantity+1" in update_query
            assert params == (query_mock.from_user.id, 'prod1')
            
            # Verify response
            print_info("Verifying user received confirmation")
            query_mock.answer.assert_called_once_with('Added to cart!')
            
            print_success("All assertions passed - test successful")
    
    @pytest.mark.asyncio
    async def test_remove_from_cart(self):
        """Test removing an item from cart"""
        print_header("Testing remove from cart")
        
        # Setup mock
        query_mock = AsyncMock(spec=types.CallbackQuery)
        query_mock.from_user.id = 12345
        query_mock.message = AsyncMock(spec=types.Message)
        callback_data = {'id': 'prod1', 'action': 'remove_from_cart'}
        
        with patch('src.handlers.user.cart.db') as mock_db, \
             patch('src.handlers.user.cart.process_cart') as mock_process_cart:
            
            # Execute
            print_info("User removes product from cart")
            await process_remove_from_cart(query_mock, callback_data)
            
            # Verify delete query
            print_info("Verifying delete query was executed")
            mock_db.query.assert_called_once()
            delete_query = mock_db.query.call_args[0][0]
            params = mock_db.query.call_args[0][1]
            
            assert "DELETE FROM cart" in delete_query
            assert params == (query_mock.from_user.id, 'prod1')
            
            # Verify response
            print_info("Verifying user received confirmation")
            query_mock.answer.assert_called_once_with('Removed from cart!')
            
            # Verify cart was refreshed
            print_info("Verifying cart was refreshed")
            mock_process_cart.assert_called_once_with(query_mock.message)
            
            print_success("All assertions passed - test successful")
    
    @pytest.mark.asyncio
    async def test_checkout_process(self, message_mock):
        """Test starting the checkout process"""
        print_header("Testing checkout process")
        
        # Setup mock data
        cart_items = [
            ('prod1', 'Test Product 1', 1000, 2),  # id, title, price, quantity
            ('prod2', 'Test Product 2', 2000, 1)
        ]
        
        expected_total = (1000 * 2) + (2000 * 1)  # 2 of prod1 + 1 of prod2
        
        # Expected response
        expected_text = 'Please enter your shipping address:'
        
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('src.handlers.user.cart.db') as mock_db, \
             patch('src.handlers.user.cart.CheckoutState.shipping_address.set') as mock_set_state:
            
            # Configure mock database response
            mock_db.fetchall.return_value = cart_items
            
            # Execute
            print_info("User initiates checkout process")
            await process_checkout(message_mock, mock_state)
            
            # Verify database query
            print_info("Verifying database was queried correctly")
            mock_db.fetchall.assert_called_once()
            
            # Verify state data was stored
            print_info("Verifying cart data was stored in state")
            mock_state.update_data.assert_called_once()
            state_data = mock_state.update_data.call_args[1]
            assert 'cart_items' in state_data
            assert 'total' in state_data
            assert state_data['cart_items'] == cart_items
            assert state_data['total'] == expected_total
            
            # Verify checkout state was set
            print_info("Verifying checkout state was set")
            mock_set_state.assert_called_once()
            
            # Test response text
            print_section("TEXT RESPONSE")
            response_text = message_mock.answer.call_args[0][0]
            print(f"▶ EXPECTED TEXT:\n{expected_text}")
            print(f"▶ ACTUAL TEXT:\n{response_text}")
            
            assert response_text == expected_text
            
            # Verify keyboard was provided
            print_info("Verifying cancel button was provided")
            response_markup = message_mock.answer.call_args[1].get('reply_markup')
            assert isinstance(response_markup, ReplyKeyboardMarkup)
            
            # Should have Cancel button
            assert len(response_markup.keyboard) == 1
            assert len(response_markup.keyboard[0]) == 1
            cancel_button = response_markup.keyboard[0][0]
            assert (cancel_button == '🔙 Cancel' or 
                   (hasattr(cancel_button, 'text') and cancel_button.text == '🔙 Cancel'))
            
            print_success("All assertions passed - test successful")
    
    @pytest.mark.asyncio
    async def test_checkout_empty_cart(self, message_mock):
        """Test checkout with empty cart"""
        print_header("Testing checkout with empty cart")
        
        # Expected response
        expected_text = 'Your cart is empty.'
        
        mock_state = AsyncMock(spec=FSMContext)
        
        with patch('src.handlers.user.cart.db') as mock_db, \
             patch('src.handlers.user.cart.CheckoutState.shipping_address.set') as mock_set_state:
            
            # Configure mock database response - empty cart
            mock_db.fetchall.return_value = []
            
            # Execute
            print_info("User tries to checkout with empty cart")
            await process_checkout(message_mock, mock_state)
            
            # Verify database query
            print_info("Verifying database was queried correctly")
            mock_db.fetchall.assert_called_once()
            
            # Verify state was not modified
            print_info("Verifying state was not modified")
            mock_state.update_data.assert_not_called()
            mock_set_state.assert_not_called()
            
            # Test response text
            print_section("TEXT RESPONSE")
            response_text = message_mock.answer.call_args[0][0]
            print(f"▶ EXPECTED TEXT:\n{expected_text}")
            print(f"▶ ACTUAL TEXT:\n{response_text}")
            
            assert response_text == expected_text
            
            print_success("All assertions passed - test successful") 