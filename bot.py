import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome to **Y_wordcounterbot**!\n\n"
        "Send or forward me any text message, and I will instantly "
        "provide you with the word count, character counts, and estimated reading time."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# Core text analysis logic
async def count_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Calculate metrics
    words = text.split()
    word_count = len(words)
    char_with_spaces = len(text)
    char_no_spaces = len(text.replace(" ", "").replace("\n", ""))
    
    # Estimate reading time (Average human reads ~200 words per minute)
    # WPM reading time formula: Minutes = Words / 200
    reading_time_seconds = round((word_count / 200) * 60)
    
    if reading_time_seconds < 60:
        read_time_str = f"{reading_time_seconds} seconds"
    else:
        read_time_str = f"{round(reading_time_seconds / 60, 1)} minute(s)"

    # Format the response message
    response = (
        "📊 **Text Analytics:**\n\n"
        f"📝 **Words:** {word_count}\n"
        f"🔤 **Characters (with spaces):** {char_with_spaces}\n"
        f"🚫 **Characters (no spaces):** {char_no_spaces}\n"
        f"⏱️ **Estimated Reading Time:** {read_time_str}"
    )
    
    await update.message.reply_text(response, parse_mode="Markdown")

async def main():
    # Retrieve the token safely from Render's environment variables
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not found.")
        return
        
    # Build the bot application inside the active async environment
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, count_words))
    
    print("Y_wordcounterbot is running successfully...")
    
    # Initialize and start polling cleanly for Render Background Workers
    await app.initialize()
    await app.updater.start_polling(drop_pending_updates=True)
    await app.start()
    
    # Keep the async worker alive indefinitely
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    # Force Python 3.14 to create and manage a clean event loop context
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped cleanly.")
