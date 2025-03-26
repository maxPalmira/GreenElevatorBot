#!/usr/bin/env python3
# Integration tests for webhook functionality

import json
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from src.app import dp
from aiogram import types
from src.handlers.menu import cmd_start

@pytest.fixture
def mock_message():
    """Create a mock message object that simulates a /start command"""
    message = MagicMock(spec=types.Message)
    message.from_user = types.User(
        id=12345,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="testuser",
        language_code="en"
    )
    message.chat = types.Chat(
        id=12345,
        type="private",
        username="testuser",
        first_name="Test",
        last_name="User"
    )
    message.text = "/start"
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    return message

@pytest.mark.asyncio
async def test_start_command_handler(mock_message):
    """Test that the start command handler responds correctly"""
    await cmd_start(mock_message)
    
    # Verify the handler called answer() at least once
    mock_message.answer.assert_called()
    # You can also check the content of the response
    assert "Welcome" in mock_message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_webhook_update_processing():
    """Test that an update from a webhook is processed correctly"""
    # Create update data that would come from a webhook
    update_data = {
        "update_id": 12345,
        "message": {
            "message_id": 67890,
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser",
                "language_code": "en"
            },
            "chat": {
                "id": 12345,
                "type": "private",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User"
            },
            "date": 1632312345,
            "text": "/start"
        }
    }
    
    # Create an Update object from the data
    update = types.Update(**update_data)
    
    # Mock the answer method that would be called by the handler
    with patch('aiogram.types.Message.answer', new_callable=AsyncMock) as mock_answer:
        # Process the update through the dispatcher
        await dp.process_update(update)
        
        # Verify that a response was sent
        mock_answer.assert_called()
        # Optionally verify content of the response
        # assert "Welcome" in mock_answer.call_args[0][0]

@pytest.mark.asyncio
async def test_webhook_request_simulation():
    """Test simulating an entire webhook HTTP request"""
    # Create a mock for bot.send_message that will be used in the handler
    with patch('src.loader.bot.send_message', new_callable=AsyncMock) as mock_send_message:
        # Create update data for a /start command
        update_data = {
            "update_id": 12345,
            "message": {
                "message_id": 67890,
                "from": {
                    "id": 12345,
                    "is_bot": False,
                    "first_name": "Test",
                    "last_name": "User",
                    "username": "testuser",
                    "language_code": "en"
                },
                "chat": {
                    "id": 12345,
                    "type": "private",
                    "username": "testuser",
                    "first_name": "Test",
                    "last_name": "User"
                },
                "date": 1632312345,
                "text": "/start"
            }
        }
        
        # Create an Update object
        update = types.Update(**update_data)
        
        # Process the update
        with patch('aiogram.types.Message.answer', new_callable=AsyncMock) as mock_answer:
            await dp.process_update(update)
            mock_answer.assert_called_once()
            
        # No need to check send_message as we're using message.answer in our handler

# This allows you to run these tests directly from the command line
if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 