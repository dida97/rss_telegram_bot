import os
import sqlite3
from datetime import datetime

os.makedirs("data", exist_ok=True)

conn = sqlite3.connect("data/data.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS seen_urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feed_url TEXT NOT NULL,
        article_url TEXT NOT NULL,
        detected_at TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS feed_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_name TEXT NOT NULL,
        feed_url TEXT NOT NULL UNIQUE,
        topics_of_interest TEXT NOT NULL,
        added_at TEXT NOT NULL
    )
""")


def is_url_seen(feed_url: str, article_url: str) -> bool:
    cursor.execute(
        "SELECT 1 FROM seen_urls WHERE feed_url = ? AND article_url = ?",
        (feed_url, article_url),
    )
    return cursor.fetchone() is not None


def add_seen_url(feed_url: str, article_url: str) -> None:
    detected_at = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO seen_urls (feed_url, article_url, detected_at) VALUES (?, ?, ?)",
        (feed_url, article_url, detected_at),
    )
    conn.commit()


def add_feed_source(source_name: str, feed_url: str, topics_of_interest: str) -> None:
    added_at = datetime.now().isoformat()
    cursor.execute(
        "INSERT OR IGNORE INTO feed_sources (source_name, feed_url, topics_of_interest, added_at) VALUES (?, ?, ?, ?)",
        (source_name, feed_url, topics_of_interest, added_at),
    )
    conn.commit()
