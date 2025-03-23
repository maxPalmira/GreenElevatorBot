from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from typing import Union
from src.config import ADMINS

class IsAdmin(BoundFilter):
    key = 'is_admin'  # Required for aiogram filters
    
    async def check(self, message: Union[types.Message, types.CallbackQuery]) -> bool:
        # Get the user ID from either message or callback query
        user_id = message.from_user.id if isinstance(message, types.Message) else message.message.from_user.id
        
        # Check if user is an admin
        return user_id in ADMINS
