# Created: Text constants file to store all message content in a centralized location
# Last Updated: 2024-03-20
# Changes:
# - Fixed button texts to match test expectations
# - Fixed message formats

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
    'ADMIN': 'Admin',
    'CART': '🛒 Cart',
    'DELIVERY': '🚚 Delivery Status'
}

# Welcome messages
WELCOME_MESSAGE = (
    "Welcome to Green Elevator Wholesale!\n\n"
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