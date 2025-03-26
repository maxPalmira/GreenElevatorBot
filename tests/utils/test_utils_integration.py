"""
Integration test utilities for the Green Elevator Wholesale Bot.
"""

from typing import Any, Dict, List, Optional, Union
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from unittest.mock import AsyncMock

async def send_message(bot: Bot, chat_id: int, text: str, **kwargs) -> Message:
    """
    Send a message in integration tests.
    
    Args:
        bot: The bot instance
        chat_id: The chat ID to send to
        text: The message text
        **kwargs: Additional message parameters
        
    Returns:
        Message: The sent message object
    """
    message = Message(
        message_id=1,
        date=1234567890,
        chat={"id": chat_id, "type": "private"},
        from_user={"id": chat_id, "is_bot": False, "first_name": "Test User"},
        text=text,
        **kwargs
    )
    
    # Mock the bot's send_message method
    bot.send_message = AsyncMock(return_value=message)
    
    # Send the message
    sent_message = await bot.send_message(
        chat_id=chat_id,
        text=text,
        **kwargs
    )
    
    return sent_message

async def validate_response(response: Union[Message, CallbackQuery], expected: Dict[str, Any]) -> bool:
    """
    Validate a bot response against expected values.
    
    Args:
        response: The bot's response message or callback
        expected: Dictionary of expected values to check
        
    Returns:
        bool: True if response matches expectations
    """
    if isinstance(response, Message):
        # Check message text
        if "text" in expected and response.text != expected["text"]:
            return False
            
        # Check reply markup
        if "reply_markup" in expected:
            if not response.reply_markup:
                return False
            if response.reply_markup.to_python() != expected["reply_markup"]:
                return False
                
    elif isinstance(response, CallbackQuery):
        # Check callback data
        if "data" in expected and response.data != expected["data"]:
            return False
            
    return True 