# Telegram Credit Card Generator Bot

A Python Telegram bot that generates Luhn-valid fake credit cards based on a provided BIN (Bank Identification Number). The bot generates cards with number, expiry date, and CVV, and provides them in a TXT file format.

## Features

- Supports BIN (Bank Identification Number) of 3, 4, or 6 digits
- Generates Luhn-algorithm valid card numbers
- Supports multiple card types (Visa, Mastercard, Amex)
- Bulk generation - specify how many cards you want
- Downloads cards as TXT file in format: `cardnumber|MM|YYYY|CVV`

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your bot token:

   **Option 1: Environment Variable**
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"
   ```

   **Option 2: .env file**
   - Copy `.env.example` to `.env`
   - Edit `.env` and add your bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

## Usage

1. Start the bot:
```bash
python bot.py
```

2. Open Telegram and find your bot

3. Send `/start` to see the help message

4. Send a BIN (3, 4, or 6 digits), for example:
   - `123`
   - `1234`
   - `123456`
   - `BIN: 1234`

5. When asked, specify how many cards you want to generate (e.g., `10`)

6. The bot will generate the cards and send you a TXT file

## File Format

The generated TXT file contains one card per line in the format:
```
1234567890123456|12|2026|123
1234567890123457|01|2027|456
1234567890123458|06|2026|789
```

Format: `cardnumber|MM|YYYY|CVV`

## Commands

- `/start` - Show help message and usage instructions
- `/cancel` - Cancel current operation and start over

## Card Type Detection

The bot automatically detects card types based on BIN:
- **Visa**: Starts with 4
- **Mastercard**: Starts with 51-55, or 222100-272099
- **Amex**: Starts with 34 or 37
- **Default**: 16-digit cards for unknown BINs

## Project Structure

```
telegram-card-bot/
├── bot.py              # Main bot file with handlers
├── card_generator.py   # Credit card generation logic
├── config.py          # Configuration management
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── .env.example       # Example environment file
├── .gitignore         # Git ignore file
└── temp/              # Temporary directory for generated files
```

## Limitations

- Maximum 1000 cards per request (configurable in `config.py`)
- Generated cards are for testing/educational purposes only
- Cards are NOT valid for actual payment processing
- Conversation timeout: 5 minutes (configurable)

## Security Notes

- Keep your bot token secure and never commit it to version control
- Generated cards are fake and should only be used for testing/educational purposes
- Temp files are automatically cleaned up after sending

## Troubleshooting

**Bot doesn't respond:**
- Check if bot token is correctly set
- Ensure bot is running (check console for errors)
- Make sure you've started a conversation with the bot in Telegram

**Invalid BIN error:**
- BIN must be exactly 3, 4, or 6 digits
- Make sure it contains only numbers

**File not received:**
- Check your internet connection
- Try generating fewer cards
- Check bot logs for errors

## License

This project is for educational purposes only. Generated credit cards are fake and should not be used for any fraudulent activities.
