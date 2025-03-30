# Change log: Created test file for menu handlers to match menu.py implementation
# Change log: Updated import to use consolidated menu.py file
# Change log: Updated test_utils import to use tests.utils.test_utils

import pytest
from aiogram import types
from src.handlers.menu import cmd_start, user_menu_handler, admin_menu_handler, view_orders, menu_handler
from tests.utils.test_utils import print_header
from src.utils.texts import (
    BUTTON_TEXTS,
    WELCOME_MESSAGE,
    USER_MENU_MESSAGE,
    ADMIN_MENU_MESSAGE,
    VIEW_ORDERS_MESSAGE
)
from unittest.mock import patch
import traceback
from src.config import ADMINS

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

@pytest.mark.asyncio
class TestMenuHandlers:
    """Test menu command handlers from src.handlers.user.menu"""
    
    @pytest.fixture(autouse=True)
    def setup_db_mock(self, db_mock):
        """Setup database mock for each test"""
        with patch('src.handlers.menu.db', db_mock):
            yield
    
    async def test_start_command(self, message_mock, db_mock):
        """Test the start command handler"""
        print_header("Testing /start command")
        
        # Setup mock return value
        db_mock.get_user_role.return_value = None
        # Mock setting the user role function
        db_mock.set_user_role.return_value = True
        
        # Define expected markup structure for user menu (no welcome screen)
        expected_keyboard = [
            [BUTTON_TEXTS['CATALOG']],
            [BUTTON_TEXTS['CONTACT']]
        ]
        
        await cmd_start(message_mock)
        
        # Verify that set_user_role was called with 'customer' role
        db_mock.set_user_role.assert_called_once_with(
            message_mock.from_user.id,
            'customer'
        )
        
        # Test response text
        print_section("TEXT RESPONSE")
        response_text = message_mock.answer.call_args[0][0]
        print(f"▶ EXPECTED TEXT:\n{USER_MENU_MESSAGE}")
        print(f"▶ ACTUAL TEXT:\n{response_text}")
        assert response_text == USER_MENU_MESSAGE, f"Expected user menu message to match exactly"
        
        # Test markup buttons
        print_section("BUTTONS")
        response_markup = message_mock.answer.call_args[1].get('reply_markup')
        print(f"▶ EXPECTED MARKUP:")
        print(format_keyboard(expected_keyboard))
        if response_markup:
            print(f"▶ ACTUAL MARKUP:")
            print(format_keyboard(response_markup.keyboard))
        
        try:
            assert response_markup is not None, "Expected markup to be present"
            assert len(response_markup.keyboard) == 2, "Expected two rows of buttons"
            assert len(response_markup.keyboard[0]) == 1, "Expected one button in first row"
            assert len(response_markup.keyboard[1]) == 1, "Expected one button in second row"
            
            # In the mock, buttons are represented as strings
            first_button = response_markup.keyboard[0][0]
            second_button = response_markup.keyboard[1][0]
            
            # Check if the button is a string or a KeyboardButton
            if isinstance(first_button, str):
                assert first_button == BUTTON_TEXTS['CATALOG'], "First button should be Catalog"
                assert second_button == BUTTON_TEXTS['CONTACT'], "Second button should be Contact"
            else:
                assert first_button.text == BUTTON_TEXTS['CATALOG'], "First button should be Catalog"
                assert second_button.text == BUTTON_TEXTS['CONTACT'], "Second button should be Contact"
                
        except AssertionError as e:
            print(f"Assertion error: {e}")
            traceback.print_exc()
            raise

    async def test_user_menu_command(self, message_mock, db_mock):
        """Test the menu command handler for regular users"""
        print_header("Testing /menu command for regular users")
        
        # Define expected markup structure
        expected_keyboard = [
            [BUTTON_TEXTS['CATALOG']],
            [BUTTON_TEXTS['CONTACT']]
        ]
        
        await user_menu_handler(message_mock)
        
        # Test response text
        print_section("TEXT RESPONSE")
        response_text = message_mock.answer.call_args[0][0]
        print(f"▶ EXPECTED TEXT:\n{USER_MENU_MESSAGE}")
        print(f"▶ ACTUAL TEXT:\n{response_text}")
        assert response_text == USER_MENU_MESSAGE, f"Expected menu message to match exactly"
        
        # Test markup buttons
        print_section("BUTTONS")
        response_markup = message_mock.answer.call_args[1].get('reply_markup')
        print(f"▶ EXPECTED MARKUP:")
        print(format_keyboard(expected_keyboard))
        if response_markup:
            print(f"▶ ACTUAL MARKUP:")
            print(format_keyboard(response_markup.keyboard))
        
        try:
            assert response_markup is not None, "Expected markup to be present"
            assert len(response_markup.keyboard) == 2, "Expected two rows of buttons"
            assert len(response_markup.keyboard[0]) == 1, "Expected one button in first row"
            assert len(response_markup.keyboard[1]) == 1, "Expected one button in second row"
            
            # In the mock, buttons are represented as strings
            first_button = response_markup.keyboard[0][0]
            second_button = response_markup.keyboard[1][0]
            
            # Check if the button is a string or a KeyboardButton
            if isinstance(first_button, str):
                assert first_button == BUTTON_TEXTS['CATALOG'], "First button should be Catalog"
                assert second_button == BUTTON_TEXTS['CONTACT'], "Second button should be Contact"
            else:
                assert first_button.text == BUTTON_TEXTS['CATALOG'], "First button should be Catalog"
                assert second_button.text == BUTTON_TEXTS['CONTACT'], "Second button should be Contact"
                
        except AssertionError as e:
            print(f"Assertion error: {e}")
            traceback.print_exc()
            raise

    async def test_admin_menu_command(self, message_mock, db_mock):
        """Test the menu command handler for admin users"""
        print_header("Testing /menu command for admin users")
        
        # Define expected markup structure
        expected_keyboard = [
            [BUTTON_TEXTS['ADMIN_CATALOG']],
            [BUTTON_TEXTS['ADMIN_QUESTIONS'], BUTTON_TEXTS['ADMIN_ORDERS']]
        ]
        
        # Set the user ID to an admin ID
        message_mock.from_user.id = 123456789  # Using the test admin ID from tests/config.py
        
        await admin_menu_handler(message_mock)
        
        # Test response text
        print_section("TEXT RESPONSE")
        response_text = message_mock.answer.call_args[0][0]
        print(f"▶ EXPECTED TEXT:\n{ADMIN_MENU_MESSAGE}")
        print(f"▶ ACTUAL TEXT:\n{response_text}")
        assert response_text == ADMIN_MENU_MESSAGE, f"Expected admin menu message to match exactly"
        
        # Test markup buttons
        print_section("BUTTONS")
        response_markup = message_mock.answer.call_args[1].get('reply_markup')
        print(f"▶ EXPECTED MARKUP:")
        print(format_keyboard(expected_keyboard))
        if response_markup:
            print(f"▶ ACTUAL MARKUP:")
            print(format_keyboard(response_markup.keyboard))
        
        try:
            assert response_markup is not None, "Expected markup to be present"
            assert len(response_markup.keyboard) == 2, "Expected two rows of buttons"
            assert len(response_markup.keyboard[0]) == 1, "Expected one button in first row"
            assert len(response_markup.keyboard[1]) == 2, "Expected two buttons in second row"
            
            # In the mock, buttons are represented as strings
            first_button = response_markup.keyboard[0][0]
            second_button = response_markup.keyboard[1][0]
            third_button = response_markup.keyboard[1][1]
            
            # Check if the button is a string or a KeyboardButton
            if isinstance(first_button, str):
                assert first_button == BUTTON_TEXTS['ADMIN_CATALOG'], "First button should be Admin Catalog"
                assert second_button == BUTTON_TEXTS['ADMIN_QUESTIONS'], "Second button should be Admin Questions"
                assert third_button == BUTTON_TEXTS['ADMIN_ORDERS'], "Third button should be Admin Orders"
            else:
                assert first_button.text == BUTTON_TEXTS['ADMIN_CATALOG'], "First button should be Admin Catalog"
                assert second_button.text == BUTTON_TEXTS['ADMIN_QUESTIONS'], "Second button should be Admin Questions"
                assert third_button.text == BUTTON_TEXTS['ADMIN_ORDERS'], "Third button should be Admin Orders"
                
        except AssertionError as e:
            print(f"Assertion error: {e}")
            traceback.print_exc()
            raise
            
    async def test_process_role_selection(self, message_mock, db_mock):
        """Test that role selection has been removed"""
        print_header("Testing role selection removal")
        
        # This method should no longer exist, so we test that it's been removed
        # The test will pass by default, as we're just documenting the removal
        print("The process_role_selection method should have been removed.")
        print("Role assignment is now automatic on /start command.")
        
        # If an admin starts the bot, they should still get admin privileges
        message_mock.from_user.id = ADMINS[0]  # Make sure user is in admin list
        db_mock.get_user_role.return_value = 'admin'
        
        await menu_handler(message_mock)
        
        # Should call admin_menu_handler for admin users
        assert message_mock.answer.call_args is not None, "Expected menu handler to respond"
        assert ADMIN_MENU_MESSAGE in message_mock.answer.call_args[0][0], "Expected admin menu message"
    
    async def test_view_orders(self, message_mock):
        """Test the view orders handler"""
        print_header("Testing admin view orders")
        
        await view_orders(message_mock)
        
        # Test response text
        response_text = message_mock.answer.call_args[0][0]
        print(f"▶ EXPECTED TEXT:\n{VIEW_ORDERS_MESSAGE}")
        print(f"▶ ACTUAL TEXT:\n{response_text}")
        assert response_text == VIEW_ORDERS_MESSAGE, "Expected view orders message to match exactly" 