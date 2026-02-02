import sqlite3
import threading
from typing import List, Tuple


class PersistentMemory:
    def __init__(self):
        self._lock = threading.Lock()
        self._db_path = "jarvis_memory.db"
        self._init_db()

    def _init_db(self):
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_text TEXT,
                        jarvis_text TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()

    def save(self, user_text: str, jarvis_text: str):
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    "INSERT INTO conversations (user_text, jarvis_text) VALUES (?, ?)",
                    (user_text, jarvis_text)
                )
                conn.commit()

    def fetch_last(self, n: int = 5) -> List[Tuple[str, str]]:
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(
                    "SELECT user_text, jarvis_text FROM conversations ORDER BY id DESC LIMIT ?",
                    (n,)
                )
                return list(reversed(cursor.fetchall()))
