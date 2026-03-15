import os
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from typing import List, Dict, Any

class Database:
    def __init__(self, db_path: str = "data/data.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seen_urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT NOT NULL,
                    article_url TEXT NOT NULL,
                    detected_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feed_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT NOT NULL UNIQUE,
                    feed_url TEXT NOT NULL UNIQUE,
                    topics_of_interest TEXT NOT NULL,
                    added_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def is_url_seen(self, source_name: str, article_url: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM seen_urls WHERE source_name = ? AND article_url = ?",
                (source_name, article_url),
            )
            return cursor.fetchone() is not None

    def add_seen_url(self, source_name: str, article_url: str) -> None:
        detected_at = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO seen_urls (source_name, article_url, detected_at) VALUES (?, ?, ?)",
                (source_name, article_url, detected_at),
            )
            conn.commit()

    def add_feed_source(self, source_name: str, feed_url: str, topics_of_interest: str) -> None:
        added_at = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO feed_sources (source_name, feed_url, topics_of_interest, added_at) VALUES (?, ?, ?, ?)",
                (source_name, feed_url, topics_of_interest, added_at),
            )
            conn.commit()

    def get_all_sources(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT source_name, feed_url, topics_of_interest FROM feed_sources")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
