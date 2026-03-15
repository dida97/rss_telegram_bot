import asyncio
import logging
import feedparser

from telegram.ext import ContextTypes
from config import Config
from utils.database import Database
from utils.analyzer import FeedAnalyzer

logger = logging.getLogger(__name__)

NO_TITLE_STRING = "No Title"
NO_SUMMARY_STRING = "No Summary"

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
            # Wrap synchronous network call to avoid blocking the loop
            feed = await asyncio.to_thread(feedparser.parse, feed_url)
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
            is_relevant = await analyzer.is_relevant(title, summary, criteria)

            if is_relevant:
                logger.info(f"Entry '{title}' is relevant for {source_name}. Sending to Telegram.")
                message = f"<b>[{source_name}] {title}</b>\n\n<a href='{link}'>Read more</a>"
                try:
                    await context.bot.send_message(
                        chat_id=config.telegram_chat_id,
                        text=message,
                        parse_mode="HTML"
                    )
                    db.add_seen_url(source_name, link)
                    logger.info(f"Successfully processed and stored item: {title}")
                except Exception as e:
                    logger.error(f"Failed to process {link}: {e}")
