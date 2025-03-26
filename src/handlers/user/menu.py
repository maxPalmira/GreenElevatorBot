"""
Menu handler for user commands.
Last Updated: 2024-03-20
Changes:
- Updated menu layout to match test expectations with flat button list
- Fixed welcome message format
"""

from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from src.loader import dp
from src.filters import IsUser

# Menu items
products = '🌿 Products'
contact = '☎️ Contact'

# Menu keyboard
menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=products, request_contact=False, request_location=False),
            KeyboardButton(text=contact, request_contact=False, request_location=False)
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Select from menu",
    selective=True,
    is_persistent=True
)

@dp.message_handler(IsUser(), commands=['menu'])
async def show_menu(message: Message):
    """Show the main menu."""
    await message.answer(
        'Welcome to Green Elevator Wholesale!\n\nPlease select an option',
        reply_markup=menu
    )

@dp.message_handler(IsUser(), text='🔙 Back to Menu')
async def back_to_menu(message: Message):
    """Handle back to menu button."""
    await show_menu(message) 