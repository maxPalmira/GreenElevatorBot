from aiogram.types import Message
from loader import dp, db
from .menu import delivery_status
from filters import IsUser

@dp.message_handler(IsUser(), text=delivery_status)
async def process_delivery_status(message: Message):
    # Get orders with product details for this user
    orders = db.fetchall('''
        SELECT o.id, p.title, o.quantity, o.status, o.created_at
        FROM orders o
        JOIN products p ON o.product_id = p.idx
        WHERE o.user_id = ?
        ORDER BY o.created_at DESC
    ''', (message.from_user.id,))
    
    if not orders:
        await message.answer('You have no active orders.')
        return
    
    text = '📦 Your Orders:\n\n'
    
    for order in orders:
        order_id, product_title, quantity, status, created_at = order
        text += f'''Order #{order_id}
🏷 Product: {product_title}
📊 Quantity: {quantity}
📋 Status: {status}
📅 Created: {created_at}
─────────────────
'''
    
    await message.answer(text)