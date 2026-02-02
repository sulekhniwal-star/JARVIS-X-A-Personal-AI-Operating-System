"""Timer and alarm skill for JARVIS-X - Alexa-like functionality."""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger

class TimerAlarmSkill:
    """Provides timer and alarm features similar to Alexa."""

    def __init__(self):
        self.timers_file = "jarvis_timers.json"
        self.alarms_file = "jarvis_alarms.json"

        # Load existing timers and alarms
        self.timers = self._load_timers()
        self.alarms = self._load_alarms()

        self.commands = {
            "set_timer": ["set timer", "start timer", "timer for", "remind me in"],
            "set_alarm": ["set alarm", "wake me up", "alarm for", "alarm at"],
            "cooking_timer": ["cooking timer", "timer for cooking", "oven timer", "bake timer"],
            "stop_timer": ["stop timer", "cancel timer", "end timer"],
            "snooze_alarm": ["snooze", "snooze alarm", "remind me later"],
            "list_timers": ["list timers", "show timers", "what timers", "active timers"],
            "list_alarms": ["list alarms", "show alarms", "what alarms", "active alarms"]
        }

        # Start background threads for checking timers and alarms
        self._start_timer_checker()
        self._start_alarm_checker()

    def can_handle(self, text: str) -> bool:
        """Check if this skill can handle the request."""
        text_lower = text.lower()
        for command_list in self.commands.values():
            if any(cmd in text_lower for cmd in command_list):
                return True
        return False

    def execute(self, text: str) -> str:
        """Execute timer/alarm command."""
        text_lower = text.lower()

        try:
            # Set timer
            if any(cmd in text_lower for cmd in self.commands["set_timer"]):
                return self._set_timer(text)

            # Set alarm
            elif any(cmd in text_lower for cmd in self.commands["set_alarm"]):
                return self._set_alarm(text)

            # Cooking timer
            elif any(cmd in text_lower for cmd in self.commands["cooking_timer"]):
                return self._set_cooking_timer(text)

            # Stop timer
            elif any(cmd in text_lower for cmd in self.commands["stop_timer"]):
                return self._stop_timer(text)

            # Snooze alarm
            elif any(cmd in text_lower for cmd in self.commands["snooze_alarm"]):
                return self._snooze_alarm()

            # List timers
            elif any(cmd in text_lower for cmd in self.commands["list_timers"]):
                return self._list_timers()

            # List alarms
            elif any(cmd in text_lower for cmd in self.commands["list_alarms"]):
                return self._list_alarms()

            else:
                return self._get_timer_alarm_overview()

        except Exception as e:
            logger.error(f"Timer/Alarm skill error: {e}")
            return "Sorry, I'm having trouble with timers and alarms right now."

    def _set_timer(self, text: str) -> str:
        """Set a timer."""
        try:
            duration = self._extract_duration(text)
            label = self._extract_label(text)

            if not duration:
                return "Please specify how long the timer should run. For example: 'set timer for 5 minutes'"

            # Create timer
            timer_id = f"timer_{len(self.timers) + 1}"
            end_time = datetime.now() + timedelta(seconds=duration)

            timer = {
                'id': timer_id,
                'label': label or 'Timer',
                'duration': duration,
                'end_time': end_time.isoformat(),
                'created': datetime.now().isoformat(),
                'active': True
            }

            self.timers[timer_id] = timer
            self._save_timers()

            duration_str = self._format_duration(duration)
            return f"Timer set for {duration_str}. I'll notify you when it goes off."

        except Exception as e:
            logger.error(f"Set timer error: {e}")
            return "Sorry, I couldn't set that timer."

    def _set_alarm(self, text: str) -> str:
        """Set an alarm."""
        try:
            alarm_time = self._extract_time(text)
            label = self._extract_label(text)

            if not alarm_time:
                return "Please specify when you'd like the alarm to go off. For example: 'set alarm for 7 AM' or 'wake me at 8:30'"

            # Create alarm
            alarm_id = f"alarm_{len(self.alarms) + 1}"

            alarm = {
                'id': alarm_id,
                'label': label or 'Alarm',
                'time': alarm_time.isoformat(),
                'created': datetime.now().isoformat(),
                'active': True,
                'snoozed': False
            }

            self.alarms[alarm_id] = alarm
            self._save_alarms()

            time_str = alarm_time.strftime('%I:%M %p')
            return f"Alarm set for {time_str}. I'll wake you up then."

        except Exception as e:
            logger.error(f"Set alarm error: {e}")
            return "Sorry, I couldn't set that alarm."

    def _set_cooking_timer(self, text: str) -> str:
        """Set a cooking timer."""
        try:
            duration = self._extract_duration(text)
            food_item = self._extract_food_item(text)

            if not duration:
                return "Please specify how long to cook. For example: 'cooking timer for 30 minutes'"

            # Create cooking timer
            timer_id = f"cooking_timer_{len(self.timers) + 1}"
            end_time = datetime.now() + timedelta(seconds=duration)

            label = f"Cooking {food_item}" if food_item else "Cooking Timer"

            timer = {
                'id': timer_id,
                'label': label,
                'duration': duration,
                'end_time': end_time.isoformat(),
                'created': datetime.now().isoformat(),
                'active': True,
                'type': 'cooking'
            }

            self.timers[timer_id] = timer
            self._save_timers()

            duration_str = self._format_duration(duration)
            return f"Cooking timer set for {duration_str}. I'll let you know when {food_item or 'your food'} is ready!"

        except Exception as e:
            logger.error(f"Set cooking timer error: {e}")
            return "Sorry, I couldn't set the cooking timer."

    def _stop_timer(self, text: str) -> str:
        """Stop a timer."""
        try:
            timer_id = self._extract_timer_id(text)

            if timer_id and timer_id in self.timers:
                timer = self.timers[timer_id]
                if timer['active']:
                    timer['active'] = False
                    self._save_timers()
                    return f"Timer '{timer['label']}' stopped."
                else:
                    return f"Timer '{timer['label']}' is not active."
            else:
                # Stop the most recent active timer
                active_timers = [t for t in self.timers.values() if t['active']]
                if active_timers:
                    # Sort by creation time, get most recent
                    most_recent = max(active_timers, key=lambda x: x['created'])
                    most_recent['active'] = False
                    self._save_timers()
                    return f"Timer '{most_recent['label']}' stopped."
                else:
                    return "No active timers to stop."

        except Exception as e:
            logger.error(f"Stop timer error: {e}")
            return "Sorry, I couldn't stop that timer."

    def _snooze_alarm(self) -> str:
        """Snooze the next alarm."""
        try:
            # Find the next active alarm
            active_alarms = [a for a in self.alarms.values() if a['active'] and not a.get('snoozed', False)]
            if not active_alarms:
                return "No active alarms to snooze."

            # Get the next alarm (simplified - just take the first active one)
            next_alarm = active_alarms[0]

            # Snooze for 9 minutes (like most alarms)
            snooze_time = datetime.now() + timedelta(minutes=9)
            next_alarm['time'] = snooze_time.isoformat()
            next_alarm['snoozed'] = True

            self._save_alarms()

            snooze_str = snooze_time.strftime('%I:%M %p')
            return f"Alarm snoozed until {snooze_str}."

        except Exception as e:
            logger.error(f"Snooze alarm error: {e}")
            return "Sorry, I couldn't snooze the alarm."

    def _list_timers(self) -> str:
        """List all active timers."""
        try:
            active_timers = [t for t in self.timers.values() if t['active']]

            if not active_timers:
                return "You have no active timers."

            response = f"You have {len(active_timers)} active timer(s):\\n\\n"

            for timer in active_timers:
                end_time = datetime.fromisoformat(timer['end_time'])
                time_remaining = end_time - datetime.now()

                if time_remaining.total_seconds() > 0:
                    remaining_str = self._format_duration(int(time_remaining.total_seconds()))
                    response += f"⏰ {timer['label']}: {remaining_str} remaining\\n"
                else:
                    response += f"⏰ {timer['label']}: Timer expired!\\n"

            return response

        except Exception as e:
            logger.error(f"List timers error: {e}")
            return "Sorry, I couldn't list your timers."

    def _list_alarms(self) -> str:
        """List all active alarms."""
        try:
            active_alarms = [a for a in self.alarms.values() if a['active']]

            if not active_alarms:
                return "You have no active alarms."

            response = f"You have {len(active_alarms)} active alarm(s):\\n\\n"

            for alarm in active_alarms:
                alarm_time = datetime.fromisoformat(alarm['time'])
                time_str = alarm_time.strftime('%I:%M %p')

                snooze_note = " (snoozed)" if alarm.get('snoozed', False) else ""
                response += f"⏰ {alarm['label']}: {time_str}{snooze_note}\\n"

            return response

        except Exception as e:
            logger.error(f"List alarms error: {e}")
            return "Sorry, I couldn't list your alarms."

    def _get_timer_alarm_overview(self) -> str:
        """Get timer and alarm overview."""
        active_timers = len([t for t in self.timers.values() if t['active']])
        active_alarms = len([a for a in self.alarms.values() if a['active']])

        return (f"⏰ Timer & Alarm Overview:\\n"
               f"⏰ Active timers: {active_timers}\\n"
               f"⏰ Active alarms: {active_alarms}\\n\\n"
               f"Try commands like:\\n"
               f"• 'set timer for 10 minutes'\\n"
               f"• 'set alarm for 7 AM'\\n"
               f"• 'cooking timer for 30 minutes'\\n"
               f"• 'list timers'\\n"
               f"• 'snooze'")

    def _start_timer_checker(self):
        """Start background thread to check for expired timers."""
        def check_timers():
            while True:
                try:
                    current_time = datetime.now()
                    expired_timers = []

                    for timer_id, timer in self.timers.items():
                        if timer['active']:
                            end_time = datetime.fromisoformat(timer['end_time'])
                            if current_time >= end_time:
                                # Timer expired
                                print(f"\\n⏰ TIMER EXPIRED: {timer['label']}")
                                timer['active'] = False
                                expired_timers.append(timer)

                    if expired_timers:
                        self._save_timers()

                    time.sleep(10)  # Check every 10 seconds

                except Exception as e:
                    logger.error(f"Timer checker error: {e}")
                    time.sleep(10)

        timer_thread = threading.Thread(target=check_timers, daemon=True)
        timer_thread.start()

    def _start_alarm_checker(self):
        """Start background thread to check for alarms."""
        def check_alarms():
            while True:
                try:
                    current_time = datetime.now()

                    for alarm_id, alarm in self.alarms.items():
                        if alarm['active'] and not alarm.get('snoozed', False):
                            alarm_time = datetime.fromisoformat(alarm['time'])
                            # Check if alarm time matches current time (within a minute)
                            if abs((current_time - alarm_time).total_seconds()) < 60:
                                print(f"\\n⏰ ALARM: {alarm['label']} - Time to wake up!")
                                # Reset snooze status
                                alarm['snoozed'] = False
                                self._save_alarms()

                    time.sleep(30)  # Check every 30 seconds

                except Exception as e:
                    logger.error(f"Alarm checker error: {e}")
                    time.sleep(30)

        alarm_thread = threading.Thread(target=check_alarms, daemon=True)
        alarm_thread.start()

    def _load_timers(self) -> Dict[str, Any]:
        """Load timers from file."""
        try:
            if os.path.exists(self.timers_file):
                with open(self.timers_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading timers: {e}")
        return {}

    def _save_timers(self):
        """Save timers to file."""
        try:
            with open(self.timers_file, 'w') as f:
                json.dump(self.timers, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving timers: {e}")

    def _load_alarms(self) -> Dict[str, Any]:
        """Load alarms from file."""
        try:
            if os.path.exists(self.alarms_file):
                with open(self.alarms_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading alarms: {e}")
        return {}

    def _save_alarms(self):
        """Save alarms to file."""
        try:
            with open(self.alarms_file, 'w') as f:
                json.dump(self.alarms, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving alarms: {e}")

    # Text extraction helper methods
    def _extract_duration(self, text: str) -> Optional[int]:
        """Extract duration in seconds from text."""
        import re

        # Patterns for different time units
        patterns = [
            (r'(\d+)\s*second', 1),
            (r'(\d+)\s*minute', 60),
            (r'(\d+)\s*hour', 3600),
            (r'(\d+)\s*hr', 3600),
            (r'(\d+):(\d+)', None),  # For MM:SS format
        ]

        text_lower = text.lower()

        for pattern, multiplier in patterns:
            match = re.search(pattern, text_lower)
            if match:
                if multiplier is None:  # MM:SS format
                    minutes = int(match.group(1))
                    seconds = int(match.group(2))
                    return minutes * 60 + seconds
                else:
                    return int(match.group(1)) * multiplier

        # Check for common phrases
        if 'half hour' in text_lower or '30 minutes' in text_lower:
            return 30 * 60
        elif 'quarter hour' in text_lower or '15 minutes' in text_lower:
            return 15 * 60
        elif '1 hour' in text_lower:
            return 3600

        return None

    def _extract_time(self, text: str) -> Optional[datetime]:
        """Extract time from text for alarms."""
        import re

        # Patterns for time
        patterns = [
            r'at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
            r'for (\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
            r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)'
        ]

        text_lower = text.lower()

        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.group(2) else 0
                am_pm = match.group(3).lower() if match.group(3) else None

                # Convert to 24-hour format
                if am_pm == 'pm' and hour != 12:
                    hour += 12
                elif am_pm == 'am' and hour == 12:
                    hour = 0

                # Create datetime for today at the specified time
                now = datetime.now()
                alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

                # If the time has already passed today, set it for tomorrow
                if alarm_time <= now:
                    alarm_time += timedelta(days=1)

                return alarm_time

        return None

    def _extract_label(self, text: str) -> Optional[str]:
        """Extract label/description from text."""
        import re

        # Look for quoted text
        match = re.search(r'"([^"]*)"', text)
        if match:
            return match.group(1)

        # Look for common patterns
        patterns = [
            r'called (.+)',
            r'labeled (.+)',
            r'named (.+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_food_item(self, text: str) -> Optional[str]:
        """Extract food item from cooking timer text."""
        import re

        # Look for food-related words after cooking/timer keywords
        match = re.search(r'(?:cooking|timer|bake|oven)\s+(?:timer\s+)?(?:for\s+)?(.+)', text, re.IGNORECASE)
        if match:
            food = match.group(1).strip()
            # Remove time-related words
            food = re.sub(r'\b(\d+\s*(?:minute|hour|second|min|hr|sec)s?)\b', '', food, flags=re.IGNORECASE).strip()
            return food if food else None

        return None

    def _extract_timer_id(self, text: str) -> Optional[str]:
        """Extract timer ID from text."""
        import re

        # Look for timer number
        match = re.search(r'timer\s+(\d+)', text, re.IGNORECASE)
        if match:
            return f"timer_{match.group(1)}"

        return None

    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to human-readable string."""
        if seconds < 60:
            return f"{seconds} second{'s' if seconds != 1 else ''}"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds == 0:
                return f"{minutes} minute{'s' if minutes != 1 else ''}"
            else:
                return f"{minutes}:{remaining_seconds:02d}"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
