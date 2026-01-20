import sqlite3
import threading
from datetime import datetime


class RoutinesManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._db_path = "jarvis_routines.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize routines database and table."""
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS routines (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        time TEXT,
                        task TEXT
                    )
                """)
                conn.commit()
    
    def add_routine(self, time: str, task: str):
        """Add a new routine."""
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute("INSERT INTO routines (time, task) VALUES (?, ?)", (time, task))
                conn.commit()
    
    def list_routines(self) -> list[str]:
        """List all routines."""
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute("SELECT time, task FROM routines ORDER BY time")
                return [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
    
    def check_due_tasks(self) -> list[str]:
        """Check for tasks due at current time."""
        current_time = datetime.now().strftime("%H:%M")
        
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute("SELECT task FROM routines WHERE time = ?", (current_time,))
                return [row[0] for row in cursor.fetchall()]