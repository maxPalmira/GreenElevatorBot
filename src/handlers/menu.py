"""
Menu handlers for the Green Elevator Wholesale Bot.
Last Updated: 2024-05-20
Changes:
- Fixed welcome message format
- Updated button layout to match test expectations
- Fixed role selection handling
- Fixed linter errors in keyboard markup initialization
- Fixed async/await handling with synchronous database
- Removed duplicate user menu handler
- Fixed message formats
- Fixed button layouts to match test expectations exactly
- Removed role selection from start command - users are now automatically set as customers unless they're in admin list
"""

from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from src.loader import dp, db
from src.filters import IsAdmin, IsUser
from src.utils.texts import (
    BUTTON_TEXTS,
    WELCOME_MESSAGE,
    ADMIN_MENU_MESSAGE,
    USER_MENU_MESSAGE,
    UNAUTHORIZED_ADMIN,
    ROLE_SET_ERROR,
    GENERIC_ERROR,
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
    """Handle /start command - automatically assign role and show menu"""
    user_id = message.from_user.id
    username = message.from_user.username
    
    logger.info(f"START COMMAND received from user: {username} (ID: {user_id})")
    logger.info(f"ADMINS list: {ADMINS}")
    
    # Automatically set role based on whether user is in admin list
    role = 'admin' if user_id in ADMINS else 'customer'
    logger.info(f"Setting user role to: {role}")
    
    success = db.set_user_role(user_id, role)
    
    if not success:
        logger.error(f"Failed to set role for user {username} (ID: {user_id})")
        await message.answer(ROLE_SET_ERROR)
        return
    
    logger.info(f"Role set successfully to {role}")
    
    # Show appropriate menu based on role
    if role == 'admin':
        logger.info(f"Showing admin menu to {username}")
        await admin_menu_handler(message)
    else:
        logger.info(f"Showing user menu to {username}")
        await user_menu_handler(message)

@dp.message_handler(commands=['menu'])
async def menu_handler(message: Message):
    """Handle /menu command"""
    # Check user role
    role = db.get_user_role(message.from_user.id)
    
    if role == 'admin':
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