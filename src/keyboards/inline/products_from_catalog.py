from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from src.loader import db

product_cb = CallbackData('product', 'id', 'action')


def product_markup(idx, price):
    global product_cb
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f'🛍️ Order Now ({price:,}฿/kilo)', callback_data=product_cb.new(id=idx, action='add')))
        
    return markup