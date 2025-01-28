import os
from dotenv import load_dotenv
import telebot
import random

# Load environment variables
load_dotenv()

# Initialize bot with token
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in .env file")

bot = telebot.TeleBot(BOT_TOKEN)

# Welcome messages list
WELCOME_MESSAGES = [
    "🌿 Yo! I'm your Green Elevator budtender bot! Ready to lift your spirits to new heights! Use /help to see what's growing! 🛗",
    "🌴 Sawadee krap! Your digital budtender at Green Elevator here! Let's find you the perfect buds in Koh Phangan! /help for the good stuff!",
    "🔥 High there! Green Elevator's virtual budtender at your service! Elevating your experience in Srithanu! Hit /help to see what's blazin'!",
    "🌺 Welcome to the highest spot in Koh Phangan! I'm your Green Elevator guide to the finest herbs in Thailand! /help to start the journey!"
]

# Command handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = random.choice(WELCOME_MESSAGES)
    bot.reply_to(message, welcome_msg)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
🌿 Welcome to Green Elevator - Your Premium Cannabis Dispensary in Koh Phangan! 🏝

📍 Location: 
- Srithanu foodcourt, right across from 7/11
- Look for the green elevator sign!

🤖 Bot Commands:
/start - Wake up your budtender
/help - See this helpful guide

🔜 Coming Soon:
- Live inventory updates
- Online ordering
- Strain information
- Daily specials
- Customer support

💚 Need help? Just send us a message and a human budtender will get back to you!

⏰ Store Hours: [Coming Soon]
☎️ Contact: [Coming Soon]

Stay lifted! 🛗✨
"""
    bot.reply_to(message, help_text)

# Echo handler - replies to all text messages
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

if __name__ == '__main__':
    print("Bot started...")
    bot.infinity_polling() 