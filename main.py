import logging
import feedparser

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

from config import Config
from utils.database import Database
from utils.telegram import send_telegram_message
from utils.analyzer import FeedAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

NO_TITLE_STRING = "No Title"
NO_SUMMARY_STRING = "No Summary"

# Conversation states
URL, NAME, CRITERIA, CONFIRMATION = range(4)

async def check_feeds_job(context: ContextTypes.DEFAULT_TYPE):
    """Background job to check all feeds every hour."""
    job_data = context.job.data
    db: Database = job_data["db"]
    analyzer: FeedAnalyzer = job_data["analyzer"]
    config: Config = job_data["config"]

    sources = db.get_all_sources()
    if not sources:
        logger.info("No sources configured. Skipping feed check.")
        return

    for source in sources:
        source_name = source["source_name"]
        feed_url = source["feed_url"]
        criteria = source["topics_of_interest"]

        logger.info(f"Fetching RSS feed for source: {source_name} at {feed_url}")
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            logger.error(f"Failed to parse feed for {source_name}: {e}")
            continue

        if not feed.entries:
            logger.info(f"No entries found for {source_name}.")
            continue

        for entry in feed.entries:
            link = entry.get("link")
            if not link:
                continue

            if db.is_url_seen(source_name, link):
                logger.debug(f"Skipping already seen URL: {link} for {source_name}")
                continue

            title = entry.get("title", NO_TITLE_STRING)
            summary = entry.get("summary", NO_SUMMARY_STRING)

            logger.info(f"Analyzing new entry for {source_name}: {title}")
            is_relevant = analyzer.is_relevant(title, summary, criteria)

            if is_relevant:
                logger.info(f"Entry '{title}' is relevant for {source_name}. Sending to Telegram.")
                message = f"<b>[{source_name}] {title}</b>\n\n<a href='{link}'>Read more</a>"
                try:
                    send_telegram_message(config.telegram_bot_token, config.telegram_chat_id, message)
                    db.add_seen_url(source_name, link)
                    logger.info(f"Successfully processed and stored item: {title}")
                except Exception as e:
                    logger.error(f"Failed to process {link}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hi! I am the RSS Reader bot. Use /add_source to configure a new feed.")

async def add_source_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for the URL."""
    await update.message.reply_text(
        "Let's add a new feed source. What is the RSS feed URL?\n"
        "(Send /cancel to abort at any time)"
    )
    return URL

async def add_source_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the URL and asks for the Name."""
    url = update.message.text
    context.user_data['url'] = url
    await update.message.reply_text(
        f"Got the URL: {url}\n\nNow, what should we name this source? (e.g., HackerNews)"
    )
    return NAME

async def add_source_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the Name and asks for the Criteria."""
    name = update.message.text
    context.user_data['name'] = name
    await update.message.reply_text(
        f"Source named: {name}\n\nFinally, what are the criteria or topics of interest for this feed?"
    )
    return CRITERIA

async def add_source_criteria(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the Criteria and asks for Confirmation."""
    criteria = update.message.text
    context.user_data['criteria'] = criteria
    
    reply_keyboard = [["Yes", "No"]]
    
    summary_text = (
        "Please confirm the new source details:\n"
        f"<b>URL:</b> {context.user_data['url']}\n"
        f"<b>Name:</b> {context.user_data['name']}\n"
        f"<b>Criteria:</b> {context.user_data['criteria']}\n\n"
        "Is this correct?"
    )
    
    await update.message.reply_text(
        summary_text,
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return CONFIRMATION

async def add_source_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the source if confirmed, or restarts/cancels otherwise."""
    answer = update.message.text.lower()
    
    if answer == "yes":
        db: Database = context.bot_data["db"]
        try:
            db.add_feed_source(
                source_name=context.user_data['name'],
                feed_url=context.user_data['url'],
                topics_of_interest=context.user_data['criteria']
            )
            
            # Immediately trigger a feed check for all current sources
            context.job_queue.run_once(
                check_feeds_job, 
                when=1, 
                data=context.bot_data["job_data"]
            )
            
            await update.message.reply_text(
                "Source successfully added! I am checking it right now for the first time.",
                reply_markup=ReplyKeyboardRemove(),
            )
        except Exception as e:
            logger.error(f"Failed to add source to DB: {e}")
            await update.message.reply_text(
                f"Error saving to database: {e}. Source not added.",
                reply_markup=ReplyKeyboardRemove(),
            )
        return ConversationHandler.END
    
    elif answer == "no":
        await update.message.reply_text(
            "Let's try again. What is the RSS feed URL?\n"
            "(Send /cancel to abort at any time)",
            reply_markup=ReplyKeyboardRemove()
        )
        return URL
    else:
        await update.message.reply_text("Please answer 'Yes' or 'No'.")
        return CONFIRMATION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "Canceled adding the source.", reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    try:
        config = Config.load()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    db = Database()
    analyzer = FeedAnalyzer(api_key=config.openrouter_api_key)

    application = Application.builder().token(config.telegram_bot_token).build()

    job_data = {
        "db": db,
        "analyzer": analyzer,
        "config": config,
    }

    # Pass dependencies via bot_data for handlers/jobs
    application.bot_data["db"] = db
    application.bot_data["job_data"] = job_data

    # Run check every 1 hour (3600 seconds), starting 10 seconds after bot boot
    application.job_queue.run_repeating(check_feeds_job, interval=3600, first=10, data=job_data)

    # Handlers
    application.add_handler(CommandHandler("start", start))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_source", add_source_start)],
        states={
            URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_source_url)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_source_name)],
            CRITERIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_source_criteria)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_source_confirmation)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    logger.info("Starting Telegram Bot with Job Queue...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
