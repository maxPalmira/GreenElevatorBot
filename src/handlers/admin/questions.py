from aiogram.types import Message, CallbackQuery
from src.loader import dp, db
from src.filters import IsAdmin
from src.utils.texts import BUTTON_TEXTS

@dp.message_handler(IsAdmin(), text=BUTTON_TEXTS['ADMIN_QUESTIONS'])
async def process_questions(message: Message):
    questions = db.query('''
        SELECT id, user_id, username, question, status, created_at
        FROM questions
        ORDER BY created_at DESC
    ''', fetchall=True)
    
    if len(questions) == 0:
        await message.answer('No pending questions.')
    else:
        for question in questions:
            qid, cid, usr_name, question_text, status, created_at = question
            text = f'''
❓ <b>Question #{qid}</b>
From: {usr_name}
Question: {question_text}
Status: {status}
Customer ID: {cid}
Created: {created_at}
'''
            await message.answer(text)
