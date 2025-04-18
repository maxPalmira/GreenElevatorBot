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
    try:
        # Get products with their categories
        try:
            products = db.execute('''
                SELECT p.idx, p.title, p.body, p.image, p.price, c.title as category
                FROM products p
                LEFT JOIN categories c ON p.tag = c.idx
                ORDER BY p.title
            ''', fetchall=True)
            
            # Log the query results
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Product query returned {len(products) if products else 0} results")
            
        except Exception as db_error:
            # Log database errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Database error in process_catalog: {str(db_error)}")
            await message.answer(f"Sorry, we couldn't load the product catalog due to a database error. Please try again later.")
            return
        
        if not products:
            await message.answer('No products available. Our catalog will be updated soon.')
            return
        
        await show_products(message, products)
    except Exception as e:
        # Catch any other unexpected errors
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in process_catalog: {str(e)}", exc_info=True)
        await message.answer("Sorry, an unexpected error occurred. Please try again later.")


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
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        
        # Ensure user exists in database
        user_id = message.from_user.id
        try:
            db.execute(
                'INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)',
                (user_id, message.from_user.username),
                commit=True
            )
        except Exception as db_error:
            logger.error(f"Database error in show_products (user insert): {str(db_error)}")
            # Continue anyway - this should not block showing products
        
        if not products:
            await message.answer("No products to display. Our catalog will be updated soon.")
            return
            
        products_shown = 0
        
        for product in products:
            try:
                product_id, title, description, image, price, category = product
                
                # Check if product is in user's cart
                try:
                    cart_item = db.execute(
                        'SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?',
                        (user_id, product_id),
                        fetchone=True
                    )
                except Exception as cart_error:
                    logger.error(f"Error checking cart for product {product_id}: {str(cart_error)}")
                    cart_item = None
                
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
                
                try:
                    if image:
                        await message.answer_photo(
                            photo=image,
                            caption=text,
                            reply_markup=markup
                        )
                    else:
                        await message.answer(text, reply_markup=markup)
                    products_shown += 1
                except Exception as send_error:
                    logger.error(f"Error sending product {product_id}: {str(send_error)}")
                    # Continue to next product
            except Exception as product_error:
                logger.error(f"Error processing product: {str(product_error)}")
                # Continue to next product
        
        if products_shown == 0:
            await message.answer("Sorry, there was an issue displaying the products. Please try again later.")
            
    except Exception as e:
        logger.error(f"Unexpected error in show_products: {str(e)}", exc_info=True)
        await message.answer("Sorry, an unexpected error occurred. Please try again later.")
