# Green Elevator Telegram Bot (Production)

A Telegram bot for Green Elevator cannabis dispensary in Koh Phangan, Thailand. This is the **production environment** version.

## Project Overview

- **Production Bot**: [@GreenElevatorBot](https://t.me/GreenElevatorBot)
- **Test Bot**: [@GreenElevatorBot_test](https://t.me/GreenElevatorBot_test)
- **Location**: Srithanu foodcourt, across from 7/11, Koh Phangan
- **Purpose**: Customer service, inventory updates, and dispensary information

## Technical Setup

### Local Development
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with:
BOT_TOKEN=your_bot_token_here
```

### Deployment
- **Platform**: Railway.app
- **Environment Variables Required**:
  - `BOT_TOKEN`: Telegram Bot API Token
- **Runtime**: Python 3.9.18
- **Process Type**: Worker (see Procfile)

### Repository Structure
```
├── .env                # Bot token configuration
├── .gitignore         # Git ignore patterns
├── Procfile           # Railway deployment configuration
├── README.md          # This file
├── bot.py            # Main bot logic
├── requirements.txt   # Python dependencies
└── runtime.txt       # Python version specification
```

## Features

### Current
- Random welcome messages with cannabis theme
- Basic command handlers (/start, /help)
- Location information
- Echo functionality

### Planned
- Live inventory updates
- Online ordering
- Strain information
- Daily specials
- Customer support integration

## Development Workflow

1. All changes should be tested in test environment first
2. Only deploy to production after thorough testing
3. Keep both environments in sync
4. Deploy via Railway (automatic on push)

## Environment Differences

### Production Environment (This Repo)
- Repository: GreenElevatorTelegramBot
- Bot: @GreenElevatorBot
- Purpose: Live customer interaction

### Test Environment
- Repository: GreenElevatorTelegramBot_test
- Bot: @GreenElevatorBot_test
- Purpose: Feature testing and development

## Maintenance Notes

- Both environments are deployed on Railway.app
- Each environment has its own bot token
- Changes to README don't trigger rebuilds
- Python dependencies are locked to specific versions
- Bot runs as a worker process, not a web service
- ⚠️ Always test changes in test environment first! 