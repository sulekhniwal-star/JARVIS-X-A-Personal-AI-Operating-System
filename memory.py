import json
import os
from datetime import datetime
from typing import Dict, List, Any


class JarvisMemory:
    """Advanced memory system for JARVIS with long-term and short-term storage."""
    
    def __init__(self, memory_file: str = "memory.json", max_history: int = 50):
        self.memory_file = memory_file
        self.max_history = max_history
        self.memory = self.load_memory()
        self.conversation_history = []
    
    def load_memory(self) -> Dict[str, Any]:
        """Load memory from JSON file."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._create_default_memory()
        else:
            return self._create_default_memory()
    
    def _create_default_memory(self) -> Dict[str, Any]:
        """Create enhanced default memory structure."""
        return {
            "owner": "Sulekh",
            "city": "Indore",
            "preferences": {
                "news": "technology",
                "music": "lofi",
                "language": "en-in",
                "units": "celsius",
                "voice_speed": 150
            },
            "habits": {
                "wake_time": "07:00",
                "sleep_time": "23:00",
                "favorite_apps": ["chrome", "youtube", "vs code"],
                "common_tasks": [],
                "usage_patterns": {}
            },
            "learned_responses": {},
            "contacts": {},
            "calendar": {},
            "notes": [],
            "system_stats": {}
        }
    
    def save_memory(self):
        """Save memory to JSON file."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def add_conversation(self, user_input: str, response: str, intent: str = None):
        """Add conversation to history (short-term memory)."""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response": response,
            "intent": intent
        }
        self.conversation_history.append(conversation)
        
        # Keep only recent conversations
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
    
    def get_recent_conversations(self, count: int = 5) -> List[Dict]:
        """Get recent conversations for context."""
        return self.conversation_history[-count:]
    
    def learn_preference(self, key: str, value: str):
        """Learn user preferences."""
        if "learned_responses" not in self.memory:
            self.memory["learned_responses"] = {}
        self.memory["learned_responses"][key] = value
        self.save_memory()
    
    def get_preference(self, key: str, default: str = None) -> str:
        """Get learned preference."""
        prefs = self.memory.get("preferences", {})
        learned = self.memory.get("learned_responses", {})
        return prefs.get(key) or learned.get(key, default)
    
    def add_habit(self, task: str):
        """Add common task to habits."""
        if "common_tasks" not in self.memory["habits"]:
            self.memory["habits"]["common_tasks"] = []
        if task not in self.memory["habits"]["common_tasks"]:
            self.memory["habits"]["common_tasks"].append(task)
            self.save_memory()
    
    def add_contact(self, name: str, phone: str = None, email: str = None):
        """Store contact information."""
        if "contacts" not in self.memory:
            self.memory["contacts"] = {}
        self.memory["contacts"][name.lower()] = {
            "phone": phone,
            "email": email
        }
        self.save_memory()
    
    def get_contact(self, name: str) -> Dict:
        """Retrieve contact information."""
        contacts = self.memory.get("contacts", {})
        return contacts.get(name.lower(), {})
    
    def add_note(self, note: str):
        """Add a note."""
        self.memory["notes"].append({
            "timestamp": datetime.now().isoformat(),
            "content": note
        })
        self.save_memory()
    
    def get_context_summary(self) -> str:
        """Enhanced context summary with smart suggestions."""
        owner = self.memory.get("owner", "Sir")
        city = self.memory.get("city", "")
        habits = self.memory.get("habits", {})
        recent = self.get_recent_conversations(3)
        
        # Time-based context
        current_hour = datetime.now().hour
        time_context = "morning" if 5 <= current_hour < 12 else "afternoon" if 12 <= current_hour < 17 else "evening" if 17 <= current_hour < 21 else "night"
        
        summary = f"User: {owner}, Location: {city}, Time: {time_context}. "
        
        if habits:
            apps = habits.get('favorite_apps', [])
            if apps:
                summary += f"Favorite apps: {', '.join(apps[:3])}. "
        
        if recent:
            summary += "Recent: "
            for conv in recent[-2:]:
                summary += f"'{conv['user_input']}' -> {conv.get('intent', 'unknown')}. "
        
        return summary
