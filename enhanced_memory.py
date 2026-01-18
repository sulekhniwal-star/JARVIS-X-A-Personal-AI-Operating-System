"""
Enhanced Memory System
=====================
Upgrade 3: Advanced Memory & Context
- Better short-term and long-term memory
- Context-aware responses
- Learning user patterns and preferences
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque

class EnhancedMemory:
    """Advanced memory system with SQLite backend and intelligent context management."""
    
    def __init__(self, memory_file: str = "jarvis_memory.db", json_backup: str = "memory.json"):
        self.memory_file = memory_file
        self.json_backup = json_backup
        self.conversation_buffer = deque(maxlen=50)  # Short-term memory
        self.context_window = deque(maxlen=10)  # Active context
        
        # Initialize database
        self._init_database()
        
        # Load user profile
        self.user_profile = self._load_user_profile()
        
        print(f"✅ Enhanced memory system initialized")
        print(f"📊 User: {self.user_profile.get('name', 'Unknown')}")
        print(f"📍 Location: {self.user_profile.get('location', 'Unknown')}")
    
    def _init_database(self):
        """Initialize SQLite database for persistent memory."""
        self.conn = sqlite3.connect(self.memory_file, check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_input TEXT,
                intent TEXT,
                response TEXT,
                context TEXT,
                satisfaction INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                category TEXT,
                last_updated TEXT,
                usage_count INTEGER DEFAULT 1
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                frequency INTEGER DEFAULT 1,
                last_used TEXT,
                time_of_day TEXT,
                context TEXT
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                created_at TEXT,
                remind_at TEXT,
                completed INTEGER DEFAULT 0,
                priority INTEGER DEFAULT 1
            )
        ''')
        
        self.conn.commit()
    
    def _load_user_profile(self) -> Dict[str, Any]:
        """Load user profile from preferences."""
        profile = {
            'name': 'Sir',
            'location': 'Indore',
            'timezone': 'Asia/Kolkata',
            'language': 'en-in',
            'voice_speed': 150,
            'preferred_apps': [],
            'work_hours': {'start': '09:00', 'end': '18:00'},
            'interests': []
        }
        
        # Load from database
        cursor = self.conn.execute(
            "SELECT key, value FROM user_preferences WHERE category = 'profile'"
        )
        for key, value in cursor.fetchall():
            try:
                profile[key] = json.loads(value)
            except:
                profile[key] = value
        
        return profile
    
    def add_conversation(self, user_input: str, response: str, intent: str, context: str = ""):
        """Add conversation to memory with context."""
        timestamp = datetime.now().isoformat()
        
        # Add to short-term buffer
        conversation = {
            'timestamp': timestamp,
            'user_input': user_input,
            'response': response,
            'intent': intent,
            'context': context
        }
        self.conversation_buffer.append(conversation)
        
        # Update context window
        self.context_window.append({
            'input': user_input,
            'intent': intent,
            'timestamp': timestamp
        })
        
        # Store in database
        self.conn.execute('''
            INSERT INTO conversations (timestamp, user_input, intent, response, context)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, user_input, intent, response, context))
        self.conn.commit()
        
        # Learn from interaction
        self._learn_from_interaction(user_input, intent, timestamp)
    
    def _learn_from_interaction(self, user_input: str, intent: str, timestamp: str):
        """Learn patterns from user interactions."""
        
        # Track app usage patterns
        if 'open_' in intent:
            app_name = intent.replace('open_', '')
            self._update_habit(f"use_{app_name}", timestamp)
        
        # Track time-based patterns
        hour = datetime.fromisoformat(timestamp).hour
        time_category = self._get_time_category(hour)
        self._update_habit(f"{intent}_{time_category}", timestamp)
        
        # Track command frequency
        self._update_habit(intent, timestamp)
    
    def _get_time_category(self, hour: int) -> str:
        """Categorize time of day."""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def _update_habit(self, action: str, timestamp: str):
        """Update habit tracking."""
        cursor = self.conn.execute(
            "SELECT frequency FROM habits WHERE action = ?", (action,)
        )
        result = cursor.fetchone()
        
        if result:
            # Update existing habit
            self.conn.execute('''
                UPDATE habits 
                SET frequency = frequency + 1, last_used = ?, time_of_day = ?
                WHERE action = ?
            ''', (timestamp, self._get_time_category(datetime.fromisoformat(timestamp).hour), action))
        else:
            # Create new habit
            self.conn.execute('''
                INSERT INTO habits (action, frequency, last_used, time_of_day)
                VALUES (?, 1, ?, ?)
            ''', (action, timestamp, self._get_time_category(datetime.fromisoformat(timestamp).hour)))
        
        self.conn.commit()
    
    def get_context_summary(self, depth: int = 3) -> str:
        """Get intelligent context summary."""
        if not self.context_window:
            return f"User: {self.user_profile['name']}, Location: {self.user_profile['location']}"
        
        # Recent interactions
        recent = list(self.context_window)[-depth:]
        
        # Build context
        context_parts = [
            f"User: {self.user_profile['name']}",
            f"Location: {self.user_profile['location']}"
        ]
        
        # Add recent context
        if recent:
            recent_intents = [item['intent'] for item in recent]
            context_parts.append(f"Recent actions: {', '.join(recent_intents)}")
        
        # Add time-based context
        current_hour = datetime.now().hour
        time_category = self._get_time_category(current_hour)
        context_parts.append(f"Time: {time_category}")
        
        # Add relevant habits
        common_habits = self.get_common_habits(time_category, limit=3)
        if common_habits:
            habit_names = [habit[0] for habit in common_habits]
            context_parts.append(f"Common {time_category} activities: {', '.join(habit_names)}")
        
        return ". ".join(context_parts)
    
    def get_common_habits(self, time_category: str = None, limit: int = 5) -> List[tuple]:
        """Get most common habits, optionally filtered by time."""
        query = '''
            SELECT action, frequency, last_used 
            FROM habits 
            WHERE frequency > 1
        '''
        params = []
        
        if time_category:
            query += " AND time_of_day = ?"
            params.append(time_category)
        
        query += " ORDER BY frequency DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.execute(query, params)
        return cursor.fetchall()
    
    def set_preference(self, key: str, value: Any, category: str = "general"):
        """Set user preference."""
        timestamp = datetime.now().isoformat()
        value_json = json.dumps(value) if not isinstance(value, str) else value
        
        self.conn.execute('''
            INSERT OR REPLACE INTO user_preferences 
            (key, value, category, last_updated, usage_count)
            VALUES (?, ?, ?, ?, 
                COALESCE((SELECT usage_count + 1 FROM user_preferences WHERE key = ?), 1))
        ''', (key, value_json, category, timestamp, key))
        self.conn.commit()
        
        # Update profile if it's a profile setting
        if category == "profile":
            self.user_profile[key] = value
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference."""
        cursor = self.conn.execute(
            "SELECT value FROM user_preferences WHERE key = ?", (key,)
        )
        result = cursor.fetchone()
        
        if result:
            try:
                return json.loads(result[0])
            except:
                return result[0]
        
        return default
    
    def add_reminder(self, content: str, remind_at: datetime = None, priority: int = 1):
        """Add a reminder."""
        created_at = datetime.now().isoformat()
        remind_at_str = remind_at.isoformat() if remind_at else None
        
        self.conn.execute('''
            INSERT INTO reminders (content, created_at, remind_at, priority)
            VALUES (?, ?, ?, ?)
        ''', (content, created_at, remind_at_str, priority))
        self.conn.commit()
        
        return self.conn.lastrowid
    
    def get_pending_reminders(self) -> List[Dict[str, Any]]:
        """Get pending reminders."""
        now = datetime.now().isoformat()
        cursor = self.conn.execute('''
            SELECT id, content, remind_at, priority
            FROM reminders 
            WHERE completed = 0 AND (remind_at IS NULL OR remind_at <= ?)
            ORDER BY priority DESC, remind_at ASC
        ''', (now,))
        
        reminders = []
        for row in cursor.fetchall():
            reminders.append({
                'id': row[0],
                'content': row[1],
                'remind_at': row[2],
                'priority': row[3]
            })
        
        return reminders
    
    def complete_reminder(self, reminder_id: int):
        """Mark reminder as completed."""
        self.conn.execute(
            "UPDATE reminders SET completed = 1 WHERE id = ?", (reminder_id,)
        )
        self.conn.commit()
    
    def get_conversation_history(self, limit: int = 10, intent_filter: str = None) -> List[Dict[str, Any]]:
        """Get conversation history."""
        query = '''
            SELECT timestamp, user_input, intent, response, context
            FROM conversations
        '''
        params = []
        
        if intent_filter:
            query += " WHERE intent = ?"
            params.append(intent_filter)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.execute(query, params)
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'timestamp': row[0],
                'user_input': row[1],
                'intent': row[2],
                'response': row[3],
                'context': row[4]
            })
        
        return history
    
    def get_smart_suggestions(self) -> List[str]:
        """Get smart suggestions based on patterns."""
        current_hour = datetime.now().hour
        time_category = self._get_time_category(current_hour)
        
        # Get common actions for this time
        habits = self.get_common_habits(time_category, limit=3)
        
        suggestions = []
        for action, frequency, last_used in habits:
            if action.startswith('open_'):
                app = action.replace('open_', '')
                suggestions.append(f"Open {app}")
            elif action in ['weather', 'news', 'time']:
                suggestions.append(f"Check {action}")
        
        # Add time-based suggestions
        if time_category == "morning":
            suggestions.extend(["Check weather", "Today's schedule", "Morning news"])
        elif time_category == "evening":
            suggestions.extend(["Play music", "Check emails", "Set reminders"])
        
        return suggestions[:5]
    
    def backup_to_json(self):
        """Backup memory to JSON file."""
        backup_data = {
            'user_profile': self.user_profile,
            'conversations': list(self.conversation_buffer),
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(self.json_backup, 'w') as f:
                json.dump(backup_data, f, indent=2)
            print(f"✅ Memory backed up to {self.json_backup}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
    
    def close(self):
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()