"""Life automation module for proactive assistance in JARVIS-X."""
from typing import Any
from datetime import datetime
from core.gemini_llm import GeminiLLM
from utils.goals import GoalsManager
from utils.routines import RoutinesManager


class LifeAutomation:
    """Provides proactive life automation and assistance."""
    # pylint: disable=too-few-public-methods
    def __init__(self, memory: Any, persistent_memory: Any):
        self.llm = GeminiLLM()
        self.goals_manager = GoalsManager()
        self.routines_manager = RoutinesManager()
        self.memory = memory
        self.persistent_memory = persistent_memory

    def proactive_assist(self) -> str:
        """Analyze user patterns and suggest proactive actions."""
        try:
            # Gather user data
            current_time = datetime.now().strftime("%H:%M")
            current_day = datetime.now().strftime("%A")

            # Get goals and routines
            goals = self.goals_manager.list_goals()
            routines = self.routines_manager.list_routines()

            # Get recent behavior from memory
            recent_conversations = self.persistent_memory.fetch_last(10)
            recent_context = "\n".join([
                f"User: {user}\nJarvis: {jarvis}"
                for user, jarvis in recent_conversations[-5:]
            ])

            today_routines = (
                [r for r in routines if current_time < r.split(' - ')[0]][:2]
                if routines else ['No routines']
            )
            # Build analysis prompt
            recent_activity = (
                recent_context[-500:] if recent_context else 'No recent activity'
            )
            analysis_prompt = (
                f"""Analyze this user's current situation and suggest ONE proactive action.
Current time: {current_time} on {current_day}
Active goals: {goals[:3] if goals else ['No active goals']}
Today's routines: {today_routines}
Recent activity: {recent_activity}

Based on their goals, time, and patterns, what should they focus on RIGHT NOW?
Respond with ONE specific, actionable suggestion in this format:
"work on [specific task]" or "take a break" or "prepare for [upcoming routine]"

Be concise and helpful."""
            )

            suggestion = self.llm.generate_reply(analysis_prompt, "")

            # Clean up suggestion
            suggestion = suggestion.strip().replace('"', '').lower()

            if suggestion and len(suggestion) > 5:
                return f"Sulekh, based on your goals, you should {suggestion} now. Shall I begin?"
            else:
                return ""

        except (AttributeError, ValueError, TypeError):
            return ""
