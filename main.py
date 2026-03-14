import os
import json
import requests
import feedparser
from openai import OpenAI
from pydantic import BaseModel
from dotenv import dotenv_values

from datetime import datetime
import sqlite3
os.makedirs('data', exist_ok=True)
conn = sqlite3.connect('data/data.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS seen_urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feed_url TEXT NOT NULL,
        article_url TEXT NOT NULL,
        detected_at TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS feed_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_name TEXT NOT NULL,
        feed_url TEXT NOT NULL UNIQUE,
        topics_of_interest TEXT NOT NULL,
        added_at TEXT NOT NULL
    )
''')

def is_url_seen(feed_url, article_url):
    cursor.execute(
        'SELECT 1 FROM seen_urls WHERE feed_url = ? AND article_url = ?',
        (feed_url, article_url)
    )
    return cursor.fetchone() is not None

def add_seen_url(feed_url, article_url):
    detected_at = datetime.now().isoformat()
    cursor.execute(
        'INSERT INTO seen_urls (feed_url, article_url, detected_at) VALUES (?, ?, ?)',
        (feed_url, article_url, detected_at)
    )
    conn.commit()

def add_feed_source(source_name, feed_url, topics_of_interest):
    added_at = datetime.now().isoformat()
    cursor.execute(
        'INSERT OR IGNORE INTO feed_sources (source_name, feed_url, topics_of_interest, added_at) VALUES (?, ?, ?, ?)',
        (source_name, feed_url, topics_of_interest, added_at)
    )
    conn.commit()

NO_TITLE_STRING = "No Title"
NO_SUMMARY_STRING = "No Summary"


# Configuration
env = dotenv_values()

RSS_FEED = env.get("RSS_FEED", None)
TELEGRAM_BOT_TOKEN = env.get("TELEGRAM_BOT_TOKEN", None)
TELEGRAM_CHAT_ID = env.get("TELEGRAM_CHAT_ID", None)
INTEREST_CRITERIA = env.get("INTEREST_CRITERIA", None)
OPENROUTER_API_KEY = env.get("OPENROUTER_API_KEY", None)

assert OPENROUTER_API_KEY, "Provide an Openrouter API Key."


class AnalysisResult(BaseModel):
    relevant: bool

def load_seen_urls():

    pass


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    response.raise_for_status()


def main():

    feed = feedparser.parse(RSS_FEED)

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    if not feed.entries:
        return

    for entry in feed.entries:
        link = entry.get("link")
        if not link or is_url_seen(RSS_FEED, link):
            continue

        title = entry.get("title", NO_TITLE_STRING)
        summary = entry.get("summary", NO_SUMMARY_STRING)

        prompt = f"""
        Analyze the following RSS feed item. 
        Criteria: {INTEREST_CRITERIA}
        Title: {title}
        Summary: {summary}
        Determine if it is relevant to the criteria specified by the user. 
        Respond **ONLY** with a valid **JSON** object matching **THIS EXACT SCHEMA**: {{"relevant" : bool}}
        """

        try:

            response = client.chat.completions.create(
                model="stepfun/step-3.5-flash:free",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            raw_content = response.choices[0].message.content
            # Valida e converte la stringa JSON nel modello Pydantic
            result = AnalysisResult.model_validate_json(raw_content)
            
            if result.relevant:
                message =  f"<b>{title}</b>\n\n<a href='{link}'>Read more</a>"
                send_telegram_message(message)
                add_seen_url(RSS_FEED, link)
            
        except Exception as e:
            print(f"Error processing {link}: {e}")
            print(f"Adding Back this entry to the queue")
            feed.entries.append(entry)



if __name__ == "__main__":
    main()
