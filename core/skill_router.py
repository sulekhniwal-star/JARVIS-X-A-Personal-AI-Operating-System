"""Enhanced skill routing for Jarvis assistant with multiple APIs."""

from skills.time_date import get_time_date
from skills.small_talk import handle_small_talk
from skills.system_control import open_app, shutdown_system, restart_system
from skills.entertainment import EntertainmentSkill
from skills.information import InformationSkill
from skills.productivity import ProductivitySkill
from loguru import logger

class SkillRouter:
    def __init__(self):
        """Initialize skill router with enhanced skills."""
        self.entertainment_skill = EntertainmentSkill()
        self.information_skill = InformationSkill()
        self.productivity_skill = ProductivitySkill()

    def route(self, text: str) -> str | None:
        """Route text to appropriate skill based on keywords."""
        text_lower = text.lower()

        try:
            # Enhanced skills with API integration
            if self.entertainment_skill.can_handle(text):
                return self.entertainment_skill.execute(text)

            if self.information_skill.can_handle(text):
                return self.information_skill.execute(text)

            if self.productivity_skill.can_handle(text):
                return self.productivity_skill.execute(text)

            # Original skills (backward compatibility)
            # Small talk
            response = handle_small_talk(text)
            if response:
                return response

            # Time/date
            if any(word in text_lower for word in ["time", "date", "clock"]):
                return get_time_date()

            # System control
            if "open" in text_lower:
                for app in ["chrome", "notepad", "calculator", "browser", "editor"]:
                    if app in text_lower:
                        return open_app(app)

            if "shutdown" in text_lower:
                return shutdown_system()

            if "restart" in text_lower:
                return restart_system()

            # Help command
            if any(word in text_lower for word in ["help", "what can you do", "commands"]):
                return self._get_help_message()

            return None

        except Exception as e:
            logger.error(f"Skill routing error: {e}")
            return "I encountered an error processing your request. Please try again."

    def _get_help_message(self) -> str:
        """Get help message with available commands."""
        return """Here's what I can help you with:

🎭 Entertainment:
• "Tell me a joke" - Get random jokes
• "Give me a quote" - Inspirational quotes
• "Random fact" - Interesting facts
• "Give me advice" - Random advice
• "Cat fact" - Fun cat facts
• "Show me a dog" - Cute dog pictures
• "NASA picture" - Astronomy picture of the day

📰 Information:
• "Weather in [city]" - Weather information
• "Latest news" - Current headlines
• "Bitcoin price" - Cryptocurrency prices
• "Exchange rates" - Currency conversion
• "Define [word]" - Word definitions
• "My IP address" - Your location info
• "GitHub user [username]" - GitHub profiles

📋 Productivity:
• "Add task [description]" - Create tasks
• "List my tasks" - Show active tasks
• "Complete task [number]" - Mark task done
• "Remind me to [task] in [time]" - Set reminders
• "Schedule [event] tomorrow" - Add to calendar
• "Time block 25 minutes" - Focus sessions
• "Productivity tips" - Get productivity advice

🖥️ System Control:
• "Open [app name]" - Launch applications
• "What time is it?" - Current time/date
• "Shutdown" / "Restart" - System control

Just speak naturally - I'll understand what you need!"""

    def get_available_skills(self) -> list:
        """Get list of available skills."""
        return [
            "Entertainment (jokes, quotes, facts, advice)",
            "Information (weather, news, crypto, definitions)",
            "Productivity (tasks, reminders, scheduling)",
            "System Control (apps, time, system commands)",
            "Small Talk (greetings, conversations)"
        ]
