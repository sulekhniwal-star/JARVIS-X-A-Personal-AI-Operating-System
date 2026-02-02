"""Personality management module for JARVIS-X."""


class PersonalityManager:
    """Manages personality modes and applies styling to responses."""
    def __init__(self):
        self.mode = "normal"
        self.interaction_count = 0

    def set_mode(self, mode: str):
        """Set personality mode."""
        if mode in ["normal", "boss", "fun", "savage"]:
            self.mode = mode
        else:
            self.mode = "normal"

    def auto_adjust_mode(self, memory_context: str):
        """Automatically adjust personality mode based on memory context."""
        context_lower = memory_context.lower()

        # Count fun indicators
        fun_words = ["😊", "😎", "😏", "🙄", "✨", "lol", "haha", "funny", "joke"]
        fun_count = sum(context_lower.count(word) for word in fun_words)

        # Count boss indicators
        boss_words = ["open", "do", "run", "find", "execute", "start", "launch", "get"]
        boss_count = sum(context_lower.count(word) for word in boss_words)

        # Adjust mode based on counts
        if fun_count > boss_count and fun_count > 2:
            self.mode = "fun"
        elif boss_count > fun_count and boss_count > 3:
            self.mode = "boss"
        else:
            self.mode = "normal"

    def apply_style(self, text: str) -> str:
        """Apply personality style to text."""
        if self.mode == "normal":
            return text

        elif self.mode == "boss":
            # Short, confident, formal
            text = text.replace("I think", "").replace("maybe", "").replace("possibly", "")
            if not text.endswith("."):
                text += "."
            return text

        elif self.mode == "fun":
            # Playful tone with emojis
            if "!" not in text:
                text = text.replace(".", "! 😊")
            return text + " ✨"

        elif self.mode == "savage":
            # Sarcastic but not rude
            if "I don't know" in text:
                return "Well, that's not in my database of infinite wisdom. 🙄"
            if "error" in text.lower():
                return "Oh great, something broke. How surprising. 😏"
            return text + " 😎"

        return text
