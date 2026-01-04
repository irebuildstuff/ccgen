"""
Telegram bot for generating fake credit cards based on BIN.
Uses ConversationHandler for multi-step flow: BIN → Quantity → File generation.
"""

import re
import os
from pathlib import Path
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

import config
from card_generator import validate_bin, generate_cards

# Conversation states
WAITING_FOR_QUANTITY = 1


def extract_bin(message_text: str) -> str:
    """
    Extracts BIN from message text.
    Supports formats: "123", "1234", "123456", "BIN: 1234", "bin 1234"
    """
    # Remove case-insensitive "BIN:" or "bin" prefix if present
    text = message_text.strip()
    text = re.sub(r'^(bin|BIN):?\s*', '', text, flags=re.IGNORECASE)
    
    # Extract numeric sequence (3, 4, or 6 digits)
    match = re.search(r'\d{3,6}', text)
    if match:
        return match.group(0)
    return ''


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = (
        "Welcome to the Credit Card Generator Bot!\n\n"
        "I can generate fake credit cards based on a BIN (Bank Identification Number).\n\n"
        "**Usage:**\n"
        "1. Send me a BIN (3, 4, or 6 digits)\n"
        "   Examples: `123`, `1234`, `123456`, or `BIN: 1234`\n"
        "2. I'll ask how many cards you want to generate\n"
        "3. I'll create a TXT file with all the cards and send it to you\n\n"
        "**Commands:**\n"
        "/start - Show this help message\n"
        "/cancel - Cancel current operation\n\n"
        "Send a BIN to get started!"
    )
    await update.message.reply_text(welcome_message)


async def handle_bin_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles BIN input from user.
    Extracts and validates BIN, then asks for quantity.
    """
    message_text = update.message.text
    bin = extract_bin(message_text)
    
    if not bin:
        await update.message.reply_text(
            "❌ Could not find a valid BIN in your message.\n\n"
            "Please send a BIN with 3, 4, or 6 digits.\n"
            "Examples: `123`, `1234`, `123456`, or `BIN: 1234`"
        )
        return ConversationHandler.END
    
    if not validate_bin(bin):
        await update.message.reply_text(
            f"❌ Invalid BIN: `{bin}`\n\n"
            "BIN must be exactly 3, 4, or 6 digits."
        )
        return ConversationHandler.END
    
    # Store BIN in user_data for later use
    context.user_data['bin'] = bin
    
    await update.message.reply_text(
        f"✅ BIN received: `{bin}`\n\n"
        "How many cards do you want to generate?\n"
        "(Send a number, e.g., 10)"
    )
    
    return WAITING_FOR_QUANTITY


async def handle_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles quantity input, generates cards, and sends TXT file.
    """
    try:
        quantity_text = update.message.text.strip()
        quantity = int(quantity_text)
        
        # Validate quantity
        if quantity <= 0:
            await update.message.reply_text(
                "❌ Quantity must be a positive number.\n"
                "Please send a number greater than 0."
            )
            return WAITING_FOR_QUANTITY
        
        if quantity > config.MAX_CARDS_PER_REQUEST:
            await update.message.reply_text(
                f"❌ Maximum {config.MAX_CARDS_PER_REQUEST} cards per request.\n"
                f"You requested {quantity} cards.\n"
                "Please try with a smaller number."
            )
            return WAITING_FOR_QUANTITY
        
        # Get BIN from user_data
        bin = context.user_data.get('bin')
        if not bin:
            await update.message.reply_text(
                "❌ BIN not found. Please start over by sending a BIN."
            )
            return ConversationHandler.END
        
        # Inform user that generation is in progress
        processing_msg = await update.message.reply_text(
            f"🔄 Generating {quantity} cards with BIN `{bin}`...\n"
            "This may take a moment."
        )
        
        # Generate cards
        cards = generate_cards(bin, quantity)
        
        # Create TXT file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cards_{bin}_{quantity}_{timestamp}.txt"
        filepath = config.TEMP_DIR / filename
        
        # Write cards to file
        with open(filepath, 'w', encoding='utf-8') as f:
            for card in cards:
                line = f"{card['number']}|{card['month']}|{card['year']}|{card['cvv']}\n"
                f.write(line)
        
        # Send file to user
        with open(filepath, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=filename,
                caption=f"✅ Generated {quantity} cards with BIN `{bin}`\n\n"
                        f"Format: `cardnumber|MM|YYYY|CVV`"
            )
        
        # Delete processing message
        await processing_msg.delete()
        
        # Clean up temp file
        try:
            filepath.unlink()
        except Exception:
            pass  # Ignore cleanup errors
        
        # Clear user_data
        context.user_data.clear()
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid quantity. Please send a valid number.\n"
            "Examples: 1, 10, 100"
        )
        return WAITING_FOR_QUANTITY
    except Exception as e:
        await update.message.reply_text(
            f"❌ An error occurred: {str(e)}\n"
            "Please try again or use /cancel to start over."
        )
        return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the conversation."""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Operation cancelled.\n"
        "Send a BIN to start again."
    )
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logs errors and handles exceptions."""
    print(f"Update {update} caused error {context.error}")


def main() -> None:
    """Start the bot."""
    # Check if bot token is configured
    if not config.TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not found!")
        print("Please set it as an environment variable or in a .env file.")
        return
    
    # Create application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Conversation handler for BIN → Quantity flow
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_bin_message
            )
        ],
        states={
            WAITING_FOR_QUANTITY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_quantity
                )
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
        conversation_timeout=config.CONVERSATION_TIMEOUT,
    )
    
    # Add handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    
    # Start bot
    print("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
