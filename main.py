import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

from config import Config
from utils.database import Database
from utils.analyzer import FeedAnalyzer

# Handlers and Jobs
from bot import (
    check_feeds_job,
    URL, NAME, CRITERIA, CONFIRMATION,
    start, add_source_start, add_source_url, add_source_name, add_source_criteria, add_source_confirmation, cancel
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

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
    application.run_polling()

if __name__ == "__main__":
    main()
