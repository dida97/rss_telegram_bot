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
   TELEGRAM_BOT_TOKEN="your-bot-token"
   TELEGRAM_CHAT_ID="your-chat-id"
   OPENROUTER_API_KEY="your-openrouter-key"
   ```

## Usage

Run the bot:
```
python main.py
```

## Files

- `main.py`: Main entry point and initialization
- `bot/`: Contains conversational handlers and background jobs
- `utils/`: Contains database class and LLM analyzer
- `data/data.db`: SQLite database for storing URLs and sources (generated upon run)
- `tests/`: Test scripts

## Testing

Run tests with:
```
python -m unittest discover tests
```

## License

MIT License

---
```
rss_telegram_bot
├─ README.md
├─ bot
│  ├─ __init__.py
│  ├─ handlers.py
│  └─ jobs.py
├─ config.py
├─ main.py
├─ tests
│  ├─ test_analyzer.py
│  └─ test_bot.py
└─ utils
   ├─ __init__.py
   ├─ analyzer.py
   └─ database.py

```