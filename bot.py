import os
from dotenv import load_dotenv
import telebot

# Load environment variables
load_dotenv()

# Initialize bot with token
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in .env file")

bot = telebot.TeleBot(BOT_TOKEN)

# Command handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Hi! I'm your bot. Use /help to see what I can do.")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
    
You can also send me any message and I'll echo it back!
"""
    bot.reply_to(message, help_text)

# Echo handler - replies to all text messages
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

if __name__ == '__main__':
    print("Bot started...")
    bot.infinity_polling() 