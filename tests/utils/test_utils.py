# Change log: Moved test utilities from src/utils to tests/utils
# 2024-03-26: Renamed TestResult to ComparisonResult to avoid pytest collection issues

import sys
import os
import warnings
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from colorama import init, Fore, Style, Back
from aiogram import types
from src.config import ADMINS, DATABASE_PATH, DATA_DIR
from src.utils.db import Database

# Initialize colorama for cross-platform colored output
init(autoreset=True)

@dataclass
class ComparisonResult:
    success: bool
    details: str
    actual: Dict[str, Any]
    expected: Dict[str, Any]

    def __str__(self) -> str:
        """String representation of test result"""
        if self.success:
            return f"{Fore.GREEN}✓ TEST PASSED{Style.RESET_ALL}"
        
        return f"""
{Fore.RED}✗ TEST FAILED{Style.RESET_ALL}

{Fore.YELLOW}Details:{Style.RESET_ALL}
{self.details}

{Fore.YELLOW}Expected Content:{Style.RESET_ALL}
{self._format_dict(self.expected)}

{Fore.YELLOW}Actual Content:{Style.RESET_ALL}
{self._format_dict(self.actual)}
"""

    def _format_dict(self, d: Dict[str, Any]) -> str:
        """Format dictionary for pretty printing"""
        lines = []
        for k, v in d.items():
            if isinstance(v, list):
                lines.append(f"  • {k}: {self._format_list(v)}")
            else:
                lines.append(f"  • {k}: {v}")
        return "\n".join(lines)
        
    def _format_list(self, items: List[Any]) -> str:
        """Format list items for pretty printing"""
        return "[" + ", ".join(f"'{item}'" if isinstance(item, str) else str(item) for item in items) + "]"

def print_section(text: str, color=None):
    """Print a section header."""
    # Skip TEXT RESPONSE and BUTTONS headers
    if text in ["TEXT RESPONSE", "BUTTONS"]:
        return
    
    # Use normal print if color is not available
    if color:
        print(f"\n{color} {text} {Style.RESET_ALL}")
    else:
        print(f"\n{Fore.BLUE}{Style.BRIGHT} {text} {Style.RESET_ALL}")

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} {text} {Style.RESET_ALL}\n")

def print_success(text: str):
    """Print a success message"""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_failure(text: str):
    """Print a failure message"""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_warning(text: str):
    """Print a warning message"""
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

def print_info(text: str):
    """Print an info message"""
    print(f"{Fore.CYAN}ℹ {text}{Style.RESET_ALL}")

def compare_responses(
    expected: Dict[str, Any], 
    response_text: str, 
    response_markup: Optional[types.ReplyKeyboardMarkup] = None
) -> ComparisonResult:
    """
    Compare expected response with actual response
    
    Args:
        expected: Dictionary with expected values
        response_text: Actual response text
        response_markup: Actual response markup
        
    Returns:
        ComparisonResult object with comparison results
    """
    result = {
        'success': True,
        'details': '',
        'expected': expected,
        'actual': {
            'text': response_text
        }
    }
    
    # Check if text matches
    if 'text' in expected:
        if expected['text'] != response_text:
            result['success'] = False
            result['details'] += f"Text doesn't match.\n"
    
    # Check buttons if markup is provided
    if response_markup and 'buttons' in expected:
        # Extract button texts from markup
        actual_buttons = []
        for row in response_markup.keyboard:
            row_buttons = []
            for btn in row:
                # Handle both string and KeyboardButton types
                if isinstance(btn, str):
                    row_buttons.append(btn)
                else:
                    row_buttons.append(btn.text)
            actual_buttons.append(row_buttons)
        
        result['actual']['buttons'] = actual_buttons
        
        # Check if button counts match
        if len(expected['buttons']) != len(actual_buttons):
            result['success'] = False
            result['details'] += f"Button row count doesn't match. Expected {len(expected['buttons'])}, got {len(actual_buttons)}.\n"
            
        # Check each row of buttons
        for i, expected_row in enumerate(expected['buttons']):
            if i >= len(actual_buttons):
                result['success'] = False
                result['details'] += f"Missing row {i} of buttons.\n"
                continue
                
            actual_row = actual_buttons[i]
            
            # Check if button counts in row match
            if len(expected_row) != len(actual_row):
                result['success'] = False
                result['details'] += f"Button count in row {i} doesn't match. Expected {len(expected_row)}, got {len(actual_row)}.\n"
                
            # Check each button in row
            for j, expected_button in enumerate(expected_row):
                if j >= len(actual_row):
                    result['success'] = False
                    result['details'] += f"Missing button {j} in row {i}.\n"
                    continue
                    
                actual_button = actual_row[j]
                
                # Check if button text matches
                if expected_button != actual_button:
                    result['success'] = False
                    result['details'] += f"Button text at row {i}, position {j} doesn't match. Expected '{expected_button}', got '{actual_button}'.\n"
    
    # Check for one_time_keyboard if specified
    if 'one_time_keyboard' in expected and response_markup:
        if expected['one_time_keyboard'] != response_markup.one_time_keyboard:
            result['success'] = False
            result['details'] += f"one_time_keyboard doesn't match. Expected {expected['one_time_keyboard']}, got {response_markup.one_time_keyboard}.\n"
        result['actual']['one_time_keyboard'] = response_markup.one_time_keyboard
    
    # Check for resize_keyboard if specified
    if 'resize_keyboard' in expected and response_markup:
        if expected['resize_keyboard'] != response_markup.resize_keyboard:
            result['success'] = False
            result['details'] += f"resize_keyboard doesn't match. Expected {expected['resize_keyboard']}, got {response_markup.resize_keyboard}.\n"
        result['actual']['resize_keyboard'] = response_markup.resize_keyboard
    
    # Check for selective if specified
    if 'selective' in expected and response_markup:
        if expected['selective'] != response_markup.selective:
            result['success'] = False
            result['details'] += f"selective doesn't match. Expected {expected['selective']}, got {response_markup.selective}.\n"
        result['actual']['selective'] = response_markup.selective
    
    # If no details were added, it means there were no issues
    if result['details'] == '':
        result['details'] = 'All checks passed.'
        
    return ComparisonResult(
        success=result['success'],
        details=result['details'],
        actual=result['actual'],
        expected=result['expected']
    )

def init_test_db() -> Database:
    """Initialize a test database with sample data"""
    print_info(f"Initializing test database at {DATABASE_PATH}")
    
    # Create a new Database instance
    db = Database(DATABASE_PATH)
    
    # Set up test data
    db.execute('''
    INSERT OR IGNORE INTO users (user_id, username, role)
    VALUES (12345, 'test_user', 'admin')
    ''', commit=True)
    
    # Add test product
    db.execute('''
    INSERT OR IGNORE INTO products (title, description, image, price, tag)
    VALUES ('Test Product', 'This is a test product', 'https://example.com/test.jpg', 99000, 1)
    ''', commit=True)
    
    # Add test category
    db.execute('''
    INSERT OR IGNORE INTO categories (title)
    VALUES ('🔥 Premium Strains')
    ''', commit=True)
    
    # Add test order
    db.execute('''
    INSERT OR IGNORE INTO orders (user_id, product_id, quantity, status)
    VALUES (12345, 1, 2, 'pending')
    ''', commit=True)
    
    # Add test question
    db.execute('''
    INSERT OR IGNORE INTO questions (user_id, username, question, status)
    VALUES (12345, 'test_user', 'Test question?', 'pending')
    ''', commit=True)
    
    print_success("Test database initialized successfully")
    return db 