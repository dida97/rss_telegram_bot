import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)

# Conversation states
URL, NAME, CRITERIA, CONFIRMATION = range(4)

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
        db = context.bot_data["db"]
        from bot.jobs import check_feeds_job # Import locally to avoid circular dependencies if later needed
        
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
