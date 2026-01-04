"""
Configuration module for the Telegram bot.
Handles bot token and other settings.
"""

import os
from pathlib import Path


# Get bot token from environment variable
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

if not TELEGRAM_BOT_TOKEN:
    # Try to read from .env file if environment variable is not set
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    TELEGRAM_BOT_TOKEN = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break

# Temp directory for generated files
TEMP_DIR = Path('temp')
TEMP_DIR.mkdir(exist_ok=True)

# Maximum number of cards that can be generated in one request
MAX_CARDS_PER_REQUEST = 1000

# Conversation timeout (in seconds)
CONVERSATION_TIMEOUT = 300  # 5 minutes
