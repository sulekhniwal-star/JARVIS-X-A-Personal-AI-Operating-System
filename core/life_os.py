"""Life operating system module for daily briefings and life management."""
from datetime import datetime
from utils.goals import GoalsManager
from utils.routines import RoutinesManager


class LifeOS:
    """Life operating system for managing daily briefings and life automation."""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.goals_manager = GoalsManager()
        self.routines_manager = RoutinesManager()

    def daily_briefing(self) -> str:
        """Generate daily briefing with goals, routines, and suggestions."""
        try:
            # Get current time info
            current_hour = datetime.now().hour
            if current_hour < 12:
                greeting = "Good morning Sulekh."
            elif current_hour < 18:
                greeting = "Good afternoon Sulekh."
            else:
                greeting = "Good evening Sulekh."

            briefing = [greeting]

            # Check pending goals
            goals = self.goals_manager.list_goals()
            if goals:
                briefing.append(f"You have {len(goals)} pending goals.")
            else:
                briefing.append("You have no pending goals.")

            # Find next routine
            routines = self.routines_manager.list_routines()
            current_time = datetime.now().strftime("%H:%M")

            next_routine = None
            for routine in routines:
                routine_time = routine.split(" - ")[0]
                if routine_time > current_time:
                    next_routine = routine
                    break

            if next_routine:
                briefing.append(f"Your next routine is {next_routine}.")
            else:
                briefing.append("No more routines scheduled for today.")

            # Suggest focus
            if goals:
                # Simple prioritization - suggest first goal
                first_goal = goals[0].split(". ", 1)[1] if ". " in goals[0] else goals[0]
                briefing.append(f"Suggested focus today: {first_goal}.")
            else:
                briefing.append("Consider setting some goals to stay productive.")

            return " ".join(briefing)

        except (AttributeError, ValueError, IndexError):
            return "I couldn't generate your daily briefing right now."
