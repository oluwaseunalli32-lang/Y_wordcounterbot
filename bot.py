import os
import logging
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, MessageHandler, InlineQueryHandler, filters, ContextTypes
from uuid import uuid4

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

def calculate_stats(text: str):
    words = len(text.split())
    chars = len(text)
    chars_no_space = len(text.replace(" ", ""))
    paragraphs = len([p for p in text.split("\n") if p.strip()])
    reading_time = max(1, round(words / 200)) # Estimated reading speed: 200 wpm
    return words, chars, chars_no_space, paragraphs, reading_time

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"Hello {user.first_name}! 👋\n\n"
        "I am your **Word Counter Bot**. Send me any text, or use me in **Inline Mode** ("
        f"`@{context.bot.username} <your text>`) in any chat to instantly count words, characters, paragraphs, and reading time!\n\n"
        "**Commands:**\n"
        "/start - Start the bot\n"
        "/help - How to use this bot"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 **How to Use Word Counter Bot:**\n\n"
        "1. **Direct Message:** Send or forward any message here for instant breakdown.\n"
        "2. **Inline Mode:** Type `@{context.bot.username} <your text>` in any chat box to generate quick stats without leaving your conversation.\n\n"
        "**Metrics Provided:**\n"
        "• Word & Character Count\n"
        "• Characters without spaces\n"
        "• Paragraph Count\n"
        "• Estimated Reading Time"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def count_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return
    
    words, chars, chars_no_space, paragraphs, reading_time = calculate_stats(text)
    
    response = (
        f"📊 **Text Statistics:**\n\n"
        f"• **Words:** {words:,}\n"
        f"• **Characters (with spaces):** {chars:,}\n"
        f"• **Characters (no spaces):** {chars_no_space:,}\n"
        f"• **Paragraphs:** {paragraphs:,}\n"
        f"• **Est. Reading Time:** ~{reading_time} min"
    )
    await update.message.reply_text(response, parse_mode="Markdown")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="Word Counter Bot",
                description="Type text after your bot handle to count words...",
                input_message_content=InputTextMessageContent(
                    "Please type text after the bot handle to count words (e.g., @BotUsername Hello world)."
                )
            )
        ]
    else:
        words, chars, chars_no_space, paragraphs, reading_time = calculate_stats(query)
        result_text = (
            f"📊 **Text Stats for:** _{query[:50]}..._\n\n"
            f"• **Words:** {words:,} | **Chars:** {chars:,} | **Paragraphs:** {paragraphs:,} | **Read Time:** ~{reading_time}m"
        )
        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=f"Words: {words} | Chars: {chars}",
                description=f"Click to send stats: {query[:60]}",
                input_message_content=InputTextMessageContent(result_text, parse_mode="Markdown")
            )
        ]
    
    await update.inline_query.answer(results, cache_time=1)

def main():
    if not TOKEN:
        logger.error("No BOT_TOKEN environment variable found!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, count_message))
    application.add_handler(InlineQueryHandler(inline_query))

    logger.info("Bot is starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
