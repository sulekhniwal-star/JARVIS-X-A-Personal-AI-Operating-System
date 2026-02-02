"""Enhanced productivity skill with scheduling and task management."""

import json
import os
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import threading
from loguru import logger

class ProductivitySkill:
    """Provides productivity features like scheduling, reminders, and task management."""

    def __init__(self):
        self.tasks_file = "jarvis_tasks.json"
        self.reminders_file = "jarvis_reminders.json"
        self.schedule_file = "jarvis_schedule.json"

        self.tasks = self._load_data(self.tasks_file, [])
        self.reminders = self._load_data(self.reminders_file, [])
        self.daily_schedule = self._load_data(self.schedule_file, {})

        self.commands = {
            "task": ["add task", "new task", "create task", "task", "todo"],
            "reminder": ["remind me", "reminder", "set reminder", "remember"],
            "schedule": ["schedule", "calendar", "appointment", "meeting"],
            "list_tasks": ["list tasks", "show tasks", "my tasks", "what tasks"],
            "complete_task": ["complete task", "finish task", "done task", "mark complete"],
            "productivity": ["productivity", "focus", "work mode", "deep work"],
            "time_block": ["time block", "block time", "focus time", "work session"]
        }

        # Start reminder checker in background
        self._start_reminder_checker()

    def can_handle(self, text: str) -> bool:
        """Check if this skill can handle the request."""
        text_lower = text.lower()
        for command_list in self.commands.values():
            if any(cmd in text_lower for cmd in command_list):
                return True
        return False

    def execute(self, text: str) -> str:
        """Execute productivity command."""
        text_lower = text.lower()

        try:
            # Task management
            if any(cmd in text_lower for cmd in self.commands["task"]):
                return self._handle_task(text)

            # Reminders
            elif any(cmd in text_lower for cmd in self.commands["reminder"]):
                return self._handle_reminder(text)

            # Scheduling
            elif any(cmd in text_lower for cmd in self.commands["schedule"]):
                return self._handle_schedule(text)

            # List tasks
            elif any(cmd in text_lower for cmd in self.commands["list_tasks"]):
                return self._list_tasks()

            # Complete task
            elif any(cmd in text_lower for cmd in self.commands["complete_task"]):
                return self._complete_task(text)

            # Productivity tips
            elif any(cmd in text_lower for cmd in self.commands["productivity"]):
                return self._get_productivity_tips()

            # Time blocking
            elif any(cmd in text_lower for cmd in self.commands["time_block"]):
                return self._handle_time_block(text)

            else:
                return self._get_productivity_overview()

        except Exception as e:
            logger.error(f"Productivity skill error: {e}")
            return "Sorry, I'm having trouble with productivity features right now."

    def _handle_task(self, text: str) -> str:
        """Handle task creation."""
        try:
            # Extract task description
            task_desc = self._extract_task_description(text)
            if not task_desc:
                return "Please specify what task you'd like to add."

            # Create new task
            task = {
                "id": len(self.tasks) + 1,
                "description": task_desc,
                "created": datetime.now().isoformat(),
                "completed": False,
                "priority": self._extract_priority(text),
                "due_date": self._extract_due_date(text)
            }

            self.tasks.append(task)
            self._save_data(self.tasks_file, self.tasks)

            priority_text = f" (Priority: {task['priority']})" if task['priority'] != 'medium' else ""
            due_text = f" (Due: {task['due_date']})" if task['due_date'] else ""

            return f"Task added: {task_desc}{priority_text}{due_text}"

        except Exception as e:
            logger.error(f"Task handling error: {e}")
            return "Sorry, I couldn't add that task."

    def _handle_reminder(self, text: str) -> str:
        """Handle reminder creation."""
        try:
            reminder_text = self._extract_reminder_text(text)
            reminder_time = self._extract_reminder_time(text)

            if not reminder_text:
                return "Please specify what you'd like me to remind you about."

            if not reminder_time:
                return "Please specify when you'd like to be reminded."

            reminder = {
                "id": len(self.reminders) + 1,
                "text": reminder_text,
                "time": reminder_time.isoformat(),
                "created": datetime.now().isoformat(),
                "active": True
            }

            self.reminders.append(reminder)
            self._save_data(self.reminders_file, self.reminders)

            return f"Reminder set: '{reminder_text}' at {reminder_time.strftime('%Y-%m-%d %H:%M')}"

        except Exception as e:
            logger.error(f"Reminder handling error: {e}")
            return "Sorry, I couldn't set that reminder."

    def _handle_schedule(self, text: str) -> str:
        """Handle scheduling."""
        try:
            event_desc = self._extract_event_description(text)
            event_time = self._extract_event_time(text)

            if not event_desc:
                return "Please specify what event you'd like to schedule."

            if not event_time:
                return "Please specify when you'd like to schedule this event."

            date_key = event_time.strftime('%Y-%m-%d')
            if date_key not in self.daily_schedule:
                self.daily_schedule[date_key] = []

            event = {
                "time": event_time.strftime('%H:%M'),
                "description": event_desc,
                "created": datetime.now().isoformat()
            }

            self.daily_schedule[date_key].append(event)
            self._save_data(self.schedule_file, self.daily_schedule)

            return f"Scheduled: '{event_desc}' on {event_time.strftime('%Y-%m-%d at %H:%M')}"

        except Exception as e:
            logger.error(f"Scheduling error: {e}")
            return "Sorry, I couldn't schedule that event."

    def _list_tasks(self) -> str:
        """List all active tasks."""
        try:
            active_tasks = [task for task in self.tasks if not task['completed']]

            if not active_tasks:
                return "You have no active tasks. Great job staying on top of things!"

            response = f"You have {len(active_tasks)} active tasks:\\n\\n"

            for task in active_tasks:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get('priority', 'medium'), "🟡")
                due_text = f" (Due: {task.get('due_date', 'No due date')})" if task.get('due_date') else ""
                response += f"{priority_icon} {task['id']}. {task['description']}{due_text}\\n"

            return response

        except Exception as e:
            logger.error(f"List tasks error: {e}")
            return "Sorry, I couldn't retrieve your tasks."

    def _complete_task(self, text: str) -> str:
        """Mark a task as completed."""
        try:
            task_id = self._extract_task_id(text)

            if not task_id:
                return "Please specify which task number you'd like to complete."

            for task in self.tasks:
                if task['id'] == task_id and not task['completed']:
                    task['completed'] = True
                    task['completed_date'] = datetime.now().isoformat()
                    self._save_data(self.tasks_file, self.tasks)
                    return f"Great job! Task '{task['description']}' marked as completed."

            return f"Task {task_id} not found or already completed."

        except Exception as e:
            logger.error(f"Complete task error: {e}")
            return "Sorry, I couldn't complete that task."

    def _handle_time_block(self, text: str) -> str:
        """Handle time blocking for focused work."""
        try:
            duration = self._extract_duration(text)
            activity = self._extract_activity(text)

            if not duration:
                duration = 25  # Default Pomodoro

            if not activity:
                activity = "focused work"

            end_time = datetime.now() + timedelta(minutes=duration)

            # Set a reminder for the end of the time block
            reminder = {
                "id": len(self.reminders) + 1,
                "text": f"Time block for {activity} is complete!",
                "time": end_time.isoformat(),
                "created": datetime.now().isoformat(),
                "active": True
            }

            self.reminders.append(reminder)
            self._save_data(self.reminders_file, self.reminders)

            return f"Time block started: {duration} minutes for {activity}. I'll remind you when it's done at {end_time.strftime('%H:%M')}."

        except Exception as e:
            logger.error(f"Time block error: {e}")
            return "Sorry, I couldn't set up that time block."

    def _get_productivity_tips(self) -> str:
        """Get productivity tips."""
        tips = [
            "Try the Pomodoro Technique: 25 minutes of focused work, then a 5-minute break.",
            "Use time blocking to dedicate specific hours to specific tasks.",
            "Start your day by tackling the most important task first.",
            "Minimize distractions by turning off notifications during focused work.",
            "Take regular breaks to maintain high productivity levels.",
            "Use the 2-minute rule: if something takes less than 2 minutes, do it now.",
            "Batch similar tasks together to maintain focus and efficiency.",
            "Set clear, specific goals for each work session."
        ]

        import random
        return f"Productivity tip: {random.choice(tips)}"

    def _get_productivity_overview(self) -> str:
        """Get productivity overview."""
        active_tasks = len([task for task in self.tasks if not task['completed']])
        completed_today = len([task for task in self.tasks if task.get('completed') and
                              task.get('completed_date', '').startswith(datetime.now().strftime('%Y-%m-%d'))])
        active_reminders = len([r for r in self.reminders if r['active']])

        return (f"Productivity Overview:\\n"
               f"📋 Active tasks: {active_tasks}\\n"
               f"✅ Completed today: {completed_today}\\n"
               f"⏰ Active reminders: {active_reminders}\\n\\n"
               f"You're doing great! Keep up the momentum!")

    def _start_reminder_checker(self):
        """Start background thread to check reminders."""
        def check_reminders():
            while True:
                try:
                    current_time = datetime.now()
                    for reminder in self.reminders:
                        if reminder['active']:
                            reminder_time = datetime.fromisoformat(reminder['time'])
                            if current_time >= reminder_time:
                                print(f"\\n🔔 REMINDER: {reminder['text']}")
                                reminder['active'] = False
                                self._save_data(self.reminders_file, self.reminders)

                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Reminder checker error: {e}")
                    time.sleep(60)

        reminder_thread = threading.Thread(target=check_reminders, daemon=True)
        reminder_thread.start()

    # Helper methods for data persistence
    def _load_data(self, filename: str, default: Any) -> Any:
        """Load data from JSON file."""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
        return default

    def _save_data(self, filename: str, data: Any):
        """Save data to JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")

    # Text extraction helper methods
    def _extract_task_description(self, text: str) -> Optional[str]:
        """Extract task description from text."""
        patterns = [
            r"add task (.+)",
            r"new task (.+)",
            r"create task (.+)",
        ]

        for pattern in patterns:
            import re
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_priority(self, text: str) -> str:
        """Extract priority from text."""
        if "high priority" in text.lower() or "urgent" in text.lower():
            return "high"
        elif "low priority" in text.lower():
            return "low"
        return "medium"

    def _extract_due_date(self, text: str) -> Optional[str]:
        """Extract due date from text."""
        # Simple implementation - can be enhanced
        if "tomorrow" in text.lower():
            return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        elif "next week" in text.lower():
            return (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        return None

    def _extract_reminder_text(self, text: str) -> Optional[str]:
        """Extract reminder text."""
        patterns = [
            r"remind me to (.+)",
            r"reminder (.+)",
        ]

        for pattern in patterns:
            import re
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_reminder_time(self, text: str) -> Optional[datetime]:
        """Extract reminder time from text."""
        # Simple implementation - can be enhanced with more sophisticated parsing
        if "in 1 hour" in text.lower():
            return datetime.now() + timedelta(hours=1)
        elif "in 30 minutes" in text.lower():
            return datetime.now() + timedelta(minutes=30)
        elif "tomorrow" in text.lower():
            return datetime.now().replace(hour=9, minute=0, second=0) + timedelta(days=1)
        return None

    def _extract_event_description(self, text: str) -> Optional[str]:
        """Extract event description."""
        patterns = [
            r"schedule (.+)",
            r"meeting (.+)",
            r"appointment (.+)"
        ]

        for pattern in patterns:
            import re
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_event_time(self, text: str) -> Optional[datetime]:
        """Extract event time."""
        # Simple implementation
        if "tomorrow at 2pm" in text.lower():
            return datetime.now().replace(hour=14, minute=0, second=0) + timedelta(days=1)
        elif "next monday" in text.lower():
            return datetime.now() + timedelta(days=7)
        return None

    def _extract_task_id(self, text: str) -> Optional[int]:
        """Extract task ID from text."""
        import re
        match = re.search(r"task (\\d+)", text, re.IGNORECASE)
        if match:
            return int(match.group(1))

        match = re.search(r"(\\d+)", text)
        if match:
            return int(match.group(1))
        return None

    def _extract_duration(self, text: str) -> Optional[int]:
        """Extract duration in minutes."""
        import re
        match = re.search(r"(\\d+) minutes?", text, re.IGNORECASE)
        if match:
            return int(match.group(1))

        match = re.search(r"(\\d+) hours?", text, re.IGNORECASE)
        if match:
            return int(match.group(1)) * 60
        return None

    def _extract_activity(self, text: str) -> Optional[str]:
        """Extract activity description."""
        patterns = [
            r"time block for (.+)",
            r"focus on (.+)",
            r"work on (.+)"
        ]

        for pattern in patterns:
            import re
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""
