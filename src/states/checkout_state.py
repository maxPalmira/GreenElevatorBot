"""
Checkout states for the cart process.
Last Updated: 2024-03-20
Changes:
- Added shipping_address state
- Removed unused states
"""

from aiogram.dispatcher.filters.state import StatesGroup, State

class CheckoutState(StatesGroup):
    """States for the checkout process."""
    shipping_address = State()  # State for collecting shipping address