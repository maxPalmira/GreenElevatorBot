"""
Menu handlers for the Green Elevator Wholesale Bot.
Changes:
1. Removed unnecessary role selection
2. Simplified menu logic to only check against ADMINS list
3. Fixed button layouts
4. Improved error handling
"""

from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from src.loader import dp, db
from src.filters import IsAdmin, IsUser
from src.utils.texts import (
    BUTTON_TEXTS,
    WELCOME_MESSAGE,
    ADMIN_MENU_MESSAGE,
    USER_MENU_MESSAGE,
    VIEW_ORDERS_MESSAGE
)
import logging
from src.config import ADMINS

logger = logging.getLogger(__name__)

# Create user menu markup
user_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Select an option",
    selective=True,
    is_persistent=True
)
user_menu.row(KeyboardButton('🌿 Products', request_contact=False, request_location=False))
user_menu.row(KeyboardButton('☎️ Contact', request_contact=False, request_location=False))

# Create admin menu markup
admin_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Select an admin option",
    selective=True,
    is_persistent=True
)
admin_menu.row(KeyboardButton(BUTTON_TEXTS['ADMIN_CATALOG'], request_contact=False, request_location=False))
admin_menu.row(
    KeyboardButton(BUTTON_TEXTS['ADMIN_QUESTIONS'], request_contact=False, request_location=False),
    KeyboardButton(BUTTON_TEXTS['ADMIN_ORDERS'], request_contact=False, request_location=False)
)

@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    """Handle /start command"""
    if message.from_user.id in ADMINS:
        logger.info(f"Admin user @{message.from_user.username} (ID: {message.from_user.id}) started bot")
        await admin_menu_handler(message)
    else:
        logger.info(f"User @{message.from_user.username} (ID: {message.from_user.id}) started bot")
        await user_menu_handler(message)

@dp.message_handler(commands=['menu'])
async def menu_handler(message: Message):
    """Handle /menu command"""
    if message.from_user.id in ADMINS:
        await admin_menu_handler(message)
    else:
        await user_menu_handler(message)

@dp.message_handler(IsUser(), commands=['menu'])
async def user_menu_handler(message: Message):
    """Handle user menu command"""
    logger.info(f"User menu requested by @{message.from_user.username} (ID: {message.from_user.id})")
    try:
        await message.answer(USER_MENU_MESSAGE, reply_markup=user_menu)
        logger.info(f"User menu sent to @{message.from_user.username}")
    except Exception as e:
        logger.error(f"Error in user menu handler: {e}")

@dp.message_handler(IsAdmin(), commands=['menu'])
async def admin_menu_handler(message: Message):
    """Handle admin menu command"""
    logger.info(f"Admin menu requested by @{message.from_user.username} (ID: {message.from_user.id})")
    try:
        await message.answer(ADMIN_MENU_MESSAGE, reply_markup=admin_menu)
        logger.info(f"Admin menu sent to @{message.from_user.username}")
    except Exception as e:
        logger.error(f"Error in admin menu handler: {e}")

@dp.message_handler(IsAdmin(), text=BUTTON_TEXTS['ADMIN_ORDERS'])
async def view_orders(message: Message):
    """Handle admin orders view"""
    logger.info(f"View Orders requested by admin {message.from_user.username} (ID: {message.from_user.id})")
    try:
        await message.answer(VIEW_ORDERS_MESSAGE)
        logger.info(f"Orders list sent to {message.from_user.username}")
    except Exception as e:
        logger.error(f"Error in view_orders handler: {e}")