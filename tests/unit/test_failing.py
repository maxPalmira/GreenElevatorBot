import pytest
from aiogram import types
from tests.utils.test_utils import compare_responses, print_header, print_info, print_success

@pytest.mark.asyncio
class TestFailingExample:
    """Example of failing tests to verify test runner output"""
    
    async def test_failing_comparison(self, message_mock):
        """Test that deliberately fails to show actual vs expected output"""
        print_header("Testing failing comparison")
        
        try:
            # Define expected content
            expected_content = {
                "greeting": "Expected greeting",
                "description": "Expected description",
                "buttons": ["Button1", "Button2"]
            }
            
            # Define actual content (different from expected)
            actual_text = "Actual greeting text with different content"
            
            # Create a mock markup with different buttons
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, selective=False, is_persistent=False, input_field_placeholder="")
            markup.add(types.KeyboardButton("DifferentButton", request_contact=False, request_location=False))
            
            # Set up the mock to return our values
            message_mock.answer.return_value = None
            message_mock.answer.call_args = ((actual_text,), {"reply_markup": markup})
            
            # Get actual response from the mock
            response_text = message_mock.answer.call_args[0][0]
            response_markup = message_mock.answer.call_args[1].get('reply_markup')
            
            # Print actual response for the test runner to capture
            print(f"\nACTUAL_RESPONSE: {response_text}")
            print(f"ACTUAL_MARKUP: {response_markup}")
            
            # Compare and report - this should fail
            result = compare_responses(expected_content, response_text, response_markup)
            assert result.success, str(result)
            
        except Exception as e:
            pytest.fail(f"Test failed as expected: {str(e)}") 