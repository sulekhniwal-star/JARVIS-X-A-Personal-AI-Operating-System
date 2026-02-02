"""Intent classification module for JARVIS-X."""
import re


class IntentClassifier:
    """Classifies user intents based on keyword patterns."""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.time_pattern = re.compile(
            r'\b(time|date|clock|today|tomorrow|yesterday|hour|minute|second'
            r'|day|week|month|year)\b',
            re.IGNORECASE
        )
        self.system_pattern = re.compile(
            r'\b(open|launch|start|shutdown|restart|close|quit|exit|run|execute)\b',
            re.IGNORECASE
        )
        self.search_pattern = re.compile(
            r'^(search|find|look up|google|what is|who is|where is|when is|how to)\b',
            re.IGNORECASE
        )

    def classify(self, text: str) -> str:
        """Classify user intent based on keyword patterns."""
        text = text.strip()

        if self.time_pattern.search(text):
            return "time"

        if self.system_pattern.search(text):
            return "system"

        if self.search_pattern.search(text):
            return "search"

        return "chat"
