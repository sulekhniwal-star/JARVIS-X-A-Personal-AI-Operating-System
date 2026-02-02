"""Small talk skills."""

def handle_small_talk(text: str) -> str | None:
    """Handle small talk responses."""
    text_lower = text.lower()

    if "how are you" in text_lower:
        return "I'm doing well, thank you for asking!"
    elif "who are you" in text_lower or "your name" in text_lower:
        return "I'm Jarvis, your AI assistant."

    return None
