"""
Created: 2024-03-20
Last Updated: 2024-03-21
Description: Catalog handler for user interactions
Changes:
- Updated SQL queries to use consistent table references
- Fixed table aliases in queries
- Fixed linting errors
- Fixed button creation to avoid type errors
"""

from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.callback_data import CallbackData
from aiogram.types.chat import ChatActions
from src.loader import dp, db, bot
from .constants import catalog
from src.filters import IsUser
from src.keyboards.inline.categories import category_cb

# Create callback data for products
product_cb = CallbackData('product', 'id', 'action')


@dp.message_handler(IsUser(), text=catalog)
async def process_catalog(message: Message):
    """Handle catalog display request"""
    # Get products with their categories
    products = db.execute('''
        SELECT p.idx, p.title, p.body, p.image, p.price, c.title as category
        FROM products p
        LEFT JOIN categories c ON p.tag = c.idx
        ORDER BY p.title
    ''', fetchall=True)
    
    if not products:
        await message.answer('No products available.')
        return
    
    await show_products(message, products)


@dp.callback_query_handler(IsUser(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict):
    """Handle category selection"""
    category_id = callback_data['id']
    
    # Get products in the selected category
    products = db.execute('''
        SELECT p.idx, p.title, p.body, p.image, p.price, c.title as category
        FROM products p
        LEFT JOIN categories c ON p.tag = c.idx
        WHERE p.tag = ?
        ORDER BY p.title
    ''', (category_id,), fetchall=True)
    
    if not products:
        await query.answer('No products in this category')
        return
    
    await query.answer('Showing products in category')
    await show_products(query.message, products)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='add'))
async def add_product_callback_handler(query: CallbackQuery, callback_data: dict):
    """Handle product add request"""
    # Instead of adding to cart, show order instructions
    order_text = '''To place an order for this product:

1. Contact us on Telegram: @GreenElevatorWholesale
2. Specify the product and quantity needed
3. Provide your business details
4. Discuss delivery options

Our team will process your order promptly! 🚀'''

    await query.answer('Order instructions sent!')
    await query.message.answer(order_text)


async def show_products(message: Message, products):
    """Display products with their details and actions"""
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    
    # Ensure user exists in database
    user_id = message.from_user.id
    db.execute(
        'INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)',
        (user_id, message.from_user.username),
        commit=True
    )
    
    for product in products:
        product_id, title, description, image, price, category = product
        
        # Check if product is in user's cart
        cart_item = db.execute(
            'SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?',
            (user_id, product_id),
            fetchone=True
        )
        
        text = f'''🏷 <b>{title}</b>
💰 Price: ${price/100:.2f}
📦 Category: {category or 'Uncategorized'}

{description}'''
        
        markup = InlineKeyboardMarkup(row_width=2)
        if cart_item:
            quantity = cart_item[0]
            markup.add(
                InlineKeyboardButton(
                    text='➖',
                    callback_data=product_cb.new(id=product_id, action='decrease')
                ),
                InlineKeyboardButton(
                    text=f'{quantity}',
                    callback_data=product_cb.new(id=product_id, action='count')
                ),
                InlineKeyboardButton(
                    text='➕',
                    callback_data=product_cb.new(id=product_id, action='increase')
                )
            )
            markup.add(
                InlineKeyboardButton(
                    text='🗑 Remove',
                    callback_data=product_cb.new(id=product_id, action='remove_from_cart')
                )
            )
        else:
            markup.add(
                InlineKeyboardButton(
                    text='🛒 Add to Cart',
                    callback_data=product_cb.new(id=product_id, action='add_to_cart')
                )
            )
        
        if image:
            await message.answer_photo(
                photo=image,
                caption=text,
                reply_markup=markup
            )
        else:
            await message.answer(text, reply_markup=markup)
