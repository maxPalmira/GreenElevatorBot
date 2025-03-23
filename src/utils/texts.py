# Created: Text constants file to store all message content in a centralized location
# This file contains all text content used in the bot's messages

__all__ = [
    'BUTTON_TEXTS',
    'WELCOME_MESSAGE',
    'ADMIN_MENU_MESSAGE',
    'USER_MENU_MESSAGE',
    'UNAUTHORIZED_ADMIN',
    'ROLE_SET_ERROR',
    'GENERIC_ERROR',
    'VIEW_ORDERS_MESSAGE',
    'CONTACT_INFO_MESSAGE'
]

# Menu button texts
BUTTON_TEXTS = {
    'CATALOG': '🌿 Products',
    'CONTACT': '☎️ Contact',
    'ADMIN_CATALOG': '⚙️ Manage Products',
    'ADMIN_ORDERS': '📋 View Orders',
    'ADMIN_QUESTIONS': '❓ Customer Questions',
    'CUSTOMER': 'Customer',
    'ADMIN': 'Admin'
}

# Welcome messages
WELCOME_MESSAGE = (
    "👋 Welcome to Green Elevator Wholesale!\n"
    "Your premier cannabis wholesale supplier\n\n"
    "Available commands:\n"
    "/menu - Browse our products\n"
    "/contact - Get in touch with us\n\n"
    "Please select your role:"
)

# Menu messages
ADMIN_MENU_MESSAGE = 'Admin Menu - Select an option:'
USER_MENU_MESSAGE = 'Welcome to Green Elevator Wholesale!\n\nPlease select an option:'

# Error messages
UNAUTHORIZED_ADMIN = "⚠️ You are not authorized as an admin. Please select 'Customer' role."
ROLE_SET_ERROR = "❌ Error setting user role. Please try again later or contact support."
GENERIC_ERROR = "❌ An error occurred. Please try again later."

# Order related messages
VIEW_ORDERS_MESSAGE = "Here are the current orders:"

# Contact information
CONTACT_INFO_MESSAGE = (
    "📞 Contact Information\n\n"
    "Phone: +1 (555) 123-4567\n"
    "Email: contact@greenelevator.com\n"
    "Hours: Monday-Friday 9AM-5PM PST\n\n"
    "For wholesale inquiries, please contact sales@greenelevator.com"
) 