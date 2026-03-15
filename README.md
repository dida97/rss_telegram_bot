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

Run the bot interactively:
```
python main.py
```

### Daemon Deployment (Ubuntu)

To run the bot in the background as a systemd service:

1. Create a service file:
```bash
sudo nano /etc/systemd/system/rss_telegram_bot.service
```

2. Add the following configuration (adjust paths and user):
```ini
[Unit]
Description=RSS Telegram Bot
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/rss_telegram_bot
ExecStart=/path/to/virtualenv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now rss_telegram_bot.service
```

4. Manage the service:
```bash
# Stop the service
sudo systemctl stop rss_telegram_bot.service

# Restart the service
sudo systemctl restart rss_telegram_bot.service

# Check status
sudo systemctl status rss_telegram_bot.service

# View logs
sudo journalctl -u rss_telegram_bot.service -f
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