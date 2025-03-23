# Change log: Consolidated menu handlers from user/menu.py and admin/menu.py into a single file

from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
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

# Create welcome markup
welcome_markup = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Select your role",
    selective=True,
    is_persistent=False
)
welcome_markup.add(BUTTON_TEXTS['CUSTOMER'], BUTTON_TEXTS['ADMIN'])

# Create user menu markup
user_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Select an option",
    selective=True,
    is_persistent=True
)
user_menu.add(BUTTON_TEXTS['CATALOG'])
user_menu.add(BUTTON_TEXTS['CONTACT'])

# Create admin menu markup
admin_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Select an admin option",
    selective=True,
    is_persistent=True
)
admin_menu.add(BUTTON_TEXTS['ADMIN_CATALOG'])
admin_menu.add(BUTTON_TEXTS['ADMIN_QUESTIONS'], BUTTON_TEXTS['ADMIN_ORDERS'])

@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    """Handler for /start command"""
    logger.info(f"Start command received from @{message.from_user.username} (ID: {message.from_user.id})")
    try:
        # Check if user already has a role
        existing_role = db.get_user_role(message.from_user.id)
        if existing_role:
            logger.info(f"User @{message.from_user.username} already has role: {existing_role}")
            await message.answer(f"Debug: user role {existing_role}")
            if existing_role == 'admin':
                await message.answer(f"Debug: admin_menu_handler()")
                return await admin_menu_handler(message)
            else:
                await message.answer(f"Debug: user_menu_handler()")
                return await user_menu_handler(message)
        
        # New user - show welcome message
        await message.answer(
            WELCOME_MESSAGE,
            reply_markup=welcome_markup
        )
        logger.info(f"Welcome message sent successfully to @{message.from_user.username}")
    except Exception as e:
        logger.error(f"Error in start command handler: {e}")

@dp.message_handler(lambda message: message.text in [BUTTON_TEXTS['CUSTOMER'], BUTTON_TEXTS['ADMIN']])
async def process_role_selection(message: Message):
    """Handler for role selection"""
    logger.info(f"Role selection from @{message.from_user.username} (ID: {message.from_user.id}): {message.text}")
    try:
        # Verify admin role
        if message.text == BUTTON_TEXTS['ADMIN'] and message.from_user.id not in ADMINS:
            logger.warning(f"Unauthorized admin access attempt from @{message.from_user.username}")
            await message.answer(UNAUTHORIZED_ADMIN)
            return

        # Set user role
        role = 'admin' if message.text == BUTTON_TEXTS['ADMIN'] else 'customer'
        if db.set_user_role(message.from_user.id, message.from_user.username, role):
            if role == 'admin':
                await admin_menu_handler(message)
            else:
                await user_menu_handler(message)
        else:
            await message.answer(ROLE_SET_ERROR)
    except Exception as e:
        logger.error(f"Error in role selection handler: {e}")
        await message.answer(GENERIC_ERROR)

@dp.message_handler(IsAdmin(), commands='menu')
async def admin_menu_handler(message: Message):
    """Handle admin menu command"""
    logger.info(f"Admin menu requested by @{message.from_user.username} (ID: {message.from_user.id})")
    try:
        await message.answer(
            ADMIN_MENU_MESSAGE,
            reply_markup=admin_menu
        )
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

@dp.message_handler(IsUser(), commands='menu')
async def user_menu_handler(message: Message):
    """Handle user menu command"""
    logger.info(f"User menu requested by @{message.from_user.username} (ID: {message.from_user.id})")
    try:
        await message.answer(
            USER_MENU_MESSAGE,
            reply_markup=user_menu
        )
        logger.info(f"User menu sent to @{message.from_user.username}")
    except Exception as e:
        logger.error(f"Error in user menu handler: {e}") 