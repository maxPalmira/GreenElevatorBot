from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from src.loader import dp, db, bot
from src.filters import IsAdmin
from src.utils.texts import BUTTON_TEXTS
from aiogram.types.chat import ChatActions
from src.utils.db import Database

product_cb = CallbackData('product', 'id', 'action')

@dp.message_handler(IsAdmin(), text=BUTTON_TEXTS['ADMIN_CATALOG'])
async def process_products(message: Message, database: Database = None):
    # Use provided database or fallback to global db
    db_instance = database or db
    
    # Get products with their categories
    products = db_instance.execute('''
        SELECT p.*, c.title as category
        FROM (SELECT * FROM products) p
        LEFT JOIN categories c ON p.tag = c.idx
        ORDER BY p.title
    ''', fetchall=True)
    
    if not products:
        await message.answer('No products found.')
        return
    
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    
    for product in products:
        product_id, title, description, image, price, tag, category = product
        price_str = "${:.2f}".format(price/100) if price is not None else "$0.00"
        text = f'''
🏷 <b>{title}</b>
💰 Price: {price_str}
📦 Category: {category or 'Uncategorized'}

{description}
'''
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton('🗑 Delete', callback_data=product_cb.new(id=product_id, action='delete')),
            InlineKeyboardButton('✏️ Edit', callback_data=product_cb.new(id=product_id, action='edit'))
        )
        
        if image:
            await message.answer_photo(photo=image, caption=text, reply_markup=markup)
        else:
            await message.answer(text, reply_markup=markup) 