from aiogram.types import Message
from src.loader import dp, db
from src.filters import IsAdmin
from src.utils.texts import BUTTON_TEXTS

@dp.message_handler(IsAdmin(), text=BUTTON_TEXTS['ADMIN_ORDERS'])
async def process_orders(message: Message):
    # Get orders with product details
    orders = db.query('''
        SELECT id, user_id, product_id, p.title, quantity, status, created_at
        FROM orders
        JOIN products p ON product_id = p.idx
        ORDER BY created_at DESC
    ''', fetchall=True)
    
    if not orders:
        await message.answer('No orders found.')
        return
    
    for order in orders:
        order_id, user_id, product_id, product_title, quantity, status, created_at = order
        text = f'''
📦 <b>Order #{order_id}</b>
Status: {status}
Product: {product_title}
Quantity: {quantity}
User ID: {user_id}
Created: {created_at}
'''
        await message.answer(text)