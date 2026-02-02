import sqlite3
import threading


class GoalsManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._db_path = "jarvis_goals.db"
        self._init_db()

    def _init_db(self):
        """Initialize goals database and table."""
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS goals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        text TEXT,
                        done INTEGER DEFAULT 0,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()

    def add_goal(self, text: str):
        """Add a new goal."""
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute("INSERT INTO goals (text) VALUES (?)", (text,))
                conn.commit()

    def list_goals(self) -> list[str]:
        """List all active goals."""
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(
                    "SELECT id, text FROM goals WHERE done = 0 ORDER BY timestamp"
                )
                return [f"{row[0]}. {row[1]}" for row in cursor.fetchall()]

    def mark_done(self, goal_id: int):
        """Mark a goal as completed."""
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute("UPDATE goals SET done = 1 WHERE id = ?", (goal_id,))
                conn.commit()
