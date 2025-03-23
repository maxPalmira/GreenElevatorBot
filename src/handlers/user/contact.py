import logging
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from src.loader import dp, db
from .constants import contact
from src.utils.texts import CONTACT_INFO_MESSAGE

logger = logging.getLogger(__name__)

class ContactState(StatesGroup):
    """State machine for contact form"""
    question = State()

@dp.message_handler(text=contact)
async def process_contact(message: Message):
    """Handle contact request from user"""
    logger.info(f"Contact request from @{message.from_user.username} (ID: {message.from_user.id})")
    
    # Display contact information from centralized text constant
    await message.answer(CONTACT_INFO_MESSAGE)
    
    # Original functionality preserved below as comments for future implementation
    """
    try:
        # Check if user has any pending questions
        existing_questions = db.execute(
            'SELECT * FROM questions WHERE user_id = ? AND status = ?',
            (message.from_user.id, 'pending'),
            fetchall=True
        )
        
        if existing_questions and len(existing_questions) >= 3:
            await message.answer(
                'You have reached the maximum number of pending questions. '
                'Please wait for responses to your existing questions.'
            )
            logger.info(f"Contact form denied for @{message.from_user.username} - too many pending questions")
            return
        
        await ContactState.question.set()
        await message.answer(
            'Please enter your question or inquiry below.\n'
            'Our team will get back to you as soon as possible.'
        )
        logger.info(f"Contact form started for @{message.from_user.username}")
    except Exception as e:
        logger.error(f"Error in contact form handler: {e}")
        await message.answer(
            'Sorry, there was an error processing your request. '
            'Please try again later.'
        )
    """

@dp.message_handler(state=ContactState.question)
async def process_question(message: Message, state: FSMContext):
    """Handle user's question submission"""
    # This function is currently disabled as we're just showing contact info
    # Will be re-enabled when the contact form functionality is needed
    
    # End the state in case it was accidentally activated
    await state.finish()
    
    """
    logger.info(f"Question received from @{message.from_user.username}")
    try:
        # Store question in database
        db.execute(
            'INSERT INTO questions (user_id, username, question, status) VALUES (?, ?, ?, ?)',
            (message.from_user.id, message.from_user.username, message.text, 'pending'),
            commit=True
        )
        
        await message.answer(
            'Thank you for your question! Our team will review it and get back to you soon.'
        )
        logger.info(f"Question stored for @{message.from_user.username}")
        
        # Notify admins about new question
        admins = db.execute(
            'SELECT user_id FROM users WHERE role = ?',
            ('admin',),
            fetchall=True
        )
        for admin_id, in admins:
            try:
                await dp.bot.send_message(
                    admin_id,
                    f'New question from @{message.from_user.username}:\n\n{message.text}'
                )
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}")
        
        await state.finish()
    except Exception as e:
        logger.error(f"Error processing question from @{message.from_user.username}: {e}")
        await message.answer(
            'Sorry, there was an error submitting your question. '
            'Please try again later.'
        )
        await state.finish()
    """ 