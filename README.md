# RSS Telegram Bot

A Python bot that monitors RSS feeds and sends updates to a Telegram channel or user.

## Features

- Fetches and parses RSS feeds
- Sends new articles to Telegram
- Tracks seen URLs to avoid duplicates
- Easy configuration via .env file

## Requirements

- Python 3.8+
- Telegram Bot API token
- RSS feed URLs

## Setup

1. Clone the repository:
   ```
   git clone <repo-url>
   cd rss_telegram_bot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure environment variables in .env:
   ```
   TELEGRAM_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   RSS_FEED=https://example.com/feed1.xml,https://example.com/feed2.xml
   
   TELEGRAM_BOT_TOKEN = "your-bot-token"
   TELEGRAM_CHAT_ID = "your-chat"
   SEEN_URLS_FILE = "seen_urls.json"
    
   INTEREST_CRITERIA = "Your topics of interest."
   ```

## Usage

Run the bot:
```
python main.py
```

## Files

- main.py: Main bot logic
- seen_urls.json: Stores URLs already sent
- tests: Test scripts

## Testing

Run tests with:
```
python -m unittest discover tests
```

## License

MIT License

---