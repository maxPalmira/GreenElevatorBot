# Telegram Bot

A simple Telegram bot built with Python and pyTelegramBotAPI.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file and add your bot token:
```
BOT_TOKEN=your_bot_token_here
```

4. Run the bot:
```bash
python bot.py
```

## Features

- Basic command handlers (/start, /help)
- Echo functionality 