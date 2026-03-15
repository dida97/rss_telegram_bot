import logging
import feedparser

from config import Config
from utils.database import Database
from utils.telegram import send_telegram_message
from utils.analyzer import FeedAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

NO_TITLE_STRING = "No Title"
NO_SUMMARY_STRING = "No Summary"

def main():
    try:
        config = Config.load()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    db = Database()
    analyzer = FeedAnalyzer(api_key=config.openrouter_api_key)

    logger.info(f"Fetching RSS feed from: {config.rss_feed}")
    feed = feedparser.parse(config.rss_feed)

    if not feed.entries:
        logger.info("No entries found in the RSS feed.")
        return

    for entry in feed.entries:
        link = entry.get("link")
        if not link:
            continue
            
        if db.is_url_seen(config.rss_feed, link):
            logger.debug(f"Skipping already seen URL: {link}")
            continue

        title = entry.get("title", NO_TITLE_STRING)
        summary = entry.get("summary", NO_SUMMARY_STRING)
        
        logger.info(f"Analyzing new entry: {title}")

        is_relevant = analyzer.is_relevant(title, summary, config.interest_criteria)

        if is_relevant:
            logger.info(f"Entry '{title}' is relevant. Sending to Telegram.")
            message = f"<b>{title}</b>\n\n<a href='{link}'>Read more</a>"
            try:
                send_telegram_message(config.telegram_bot_token, config.telegram_chat_id, message)
                db.add_seen_url(config.rss_feed, link)
                logger.info(f"Successfully processed and stored item: {title}")
            except Exception as e:
                logger.error(f"Failed to process {link}: {e}")
                # We do NOT append it back to feed.entries. It simply wasn't marked as seen, 
                # so it will be retried on the next run.

if __name__ == "__main__":
    main()
