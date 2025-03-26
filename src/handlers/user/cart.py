"""
Cart handler for user commands.
Last Updated: 2024-03-20
Changes:
- Updated database interface to use execute with proper parameters
- Fixed keyboard markup initialization with proper parameters
- Fixed cart button text and keyboard layout
- Fixed database queries to match test expectations
- Fixed checkout state handling using proper method
"""

import logging
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from src.keyboards.inline.products_from_cart import product_markup, product_cb
from aiogram.utils.callback_data import CallbackData
from src.keyboards.default.markups import *
from aiogram.types.chat import ChatActions
from src.states.checkout_state import CheckoutState
from src.loader import dp, db, bot
from src.filters import IsUser

# Cart button text
cart_button = '🛒 Cart'

@dp.message_handler(IsUser(), text=cart_button)
async def process_cart(message: Message):
    # Get cart items with product details
    cart_items = db.execute('''
        SELECT p.idx, p.title, p.price, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.idx
        WHERE c.user_id = ?
        ORDER BY p.title
    ''', (message.from_user.id,), fetchall=True)
    
    if not cart_items:
        await message.answer('Your cart is empty.')
        return
    
    total = 0
    text = '🛒 Your Cart:\n\n'
    
    for item in cart_items:
        product_id, title, price, quantity = item
        item_total = price * quantity
        total += item_total
        
        text += f'''🏷 {title}
📊 Quantity: {quantity}
💰 Price: ${price/100:.2f}
💵 Subtotal: ${item_total/100:.2f}
─────────────────
'''
    
    text += f'\n💳 Total: ${total/100:.2f}'
    
    markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        selective=True,
        is_persistent=True,
        input_field_placeholder="Select an option"
    )
    markup.row('📦 Checkout')
    markup.row('🔙 Back to Menu')
    
    await message.answer(text, reply_markup=markup)

@dp.callback_query_handler(IsUser(), product_cb.filter(action='add_to_cart'))
async def process_add_to_cart(query: CallbackQuery, callback_data: dict):
    product_id = callback_data['id']
    
    # Check if product exists
    product = db.execute(
        'SELECT idx, title, body, image, price, tag FROM products WHERE idx=?',
        (product_id,),
        fetchone=True
    )
    if not product:
        await query.answer('Product not found.')
        return
    
    # Add to cart or update quantity
    cart_item = db.execute(
        'SELECT quantity FROM cart WHERE user_id=? AND product_id=?',
        (query.from_user.id, product_id),
        fetchone=True
    )
    
    if cart_item:
        # Update quantity
        db.execute(
            'UPDATE cart SET quantity=quantity+1 WHERE user_id=? AND product_id=?',
            (query.from_user.id, product_id),
            commit=True
        )
    else:
        # Add new item
        db.execute(
            'INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, 1)',
            (query.from_user.id, product_id),
            commit=True
        )
    
    await query.answer('Added to cart!')

@dp.callback_query_handler(IsUser(), product_cb.filter(action='remove_from_cart'))
async def process_remove_from_cart(query: CallbackQuery, callback_data: dict):
    product_id = callback_data['id']
    
    db.execute(
        'DELETE FROM cart WHERE user_id=? AND product_id=?',
        (query.from_user.id, product_id),
        commit=True
    )
    
    await query.answer('Removed from cart!')
    await process_cart(query.message)

@dp.message_handler(IsUser(), text='📦 Checkout')
async def process_checkout(message: Message, state: FSMContext):
    # Get cart items
    cart_items = db.execute('''
        SELECT p.idx, p.title, p.price, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.idx
        WHERE c.user_id = ?
    ''', (message.from_user.id,), fetchall=True)
    
    if not cart_items:
        await message.answer('Your cart is empty.')
        return
    
    # Calculate total
    total = sum(price * quantity for _, _, price, quantity in cart_items)
    
    # Store cart info in state
    await state.update_data(cart_items=cart_items, total=total)
    
    # Start checkout process
    await CheckoutState.shipping_address.set()
    await message.answer(
        'Please enter your shipping address:',
        reply_markup=ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
            selective=True,
            is_persistent=True,
            input_field_placeholder="Enter your shipping address"
        ).add('🔙 Cancel')
    )

@dp.message_handler(IsUser(), state=CheckoutState.shipping_address)
async def process_shipping_address(message: Message, state: FSMContext):
    if message.text == '🔙 Cancel':
        await state.finish()
        await message.answer('Checkout cancelled.', reply_markup=ReplyKeyboardRemove(selective=False))
        return
    
    # Get cart data
    data = await state.get_data()
    cart_items = data['cart_items']
    
    # Create orders for each cart item
    for product_id, title, price, quantity in cart_items:
        db.execute('''
            INSERT INTO orders (
                user_id, product_id, quantity, status
            ) VALUES (?, ?, ?, 'pending')
        ''', (message.from_user.id, product_id, quantity), commit=True)
    
    # Clear cart
    db.execute('DELETE FROM cart WHERE user_id=?', (message.from_user.id,), commit=True)
    
    # Finish checkout
    await state.finish()
    await message.answer(
        f'''✅ Order placed successfully!
        
📦 Your items will be shipped to:
{message.text}

Our team will contact you shortly to confirm the order.
''',
        reply_markup=ReplyKeyboardRemove(selective=False)
    )
