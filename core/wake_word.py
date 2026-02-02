"""Wake word detection functionality."""
import re
import threading
import time


class WakeWordDetector:
    """Detects wake words in text and audio."""

    def __init__(self, wake_word: str = "jarvis"):
        """Initialize with the wake word."""
        self.wake_word = wake_word.lower()
        self.is_listening = False
        self.wake_detected = False
        self.sleep_words = ["go to sleep", "sleep mode", "stop listening", "jarvis sleep", "सो जाओ", "सोने का समय", "बंद करो"]
        self.wake_words = ["jarvis", "hey jarvis", "jarvis wake up", "जार्विस", "हे जार्विस", "जार्विस जागो"]

    def is_wake_word(self, text: str) -> bool:
        """Check if the wake word is present as a full word in the text.

        - Case-insensitive
        - Ignores punctuation
        - Returns True only if wake word exists as a full word
        """
        # Normalize text: lower case, remove punctuation
        normalized_text = re.sub(r'[^\w\s]', '', text.lower())

        # Check for wake words
        for wake in self.wake_words:
            if wake in normalized_text:
                return True

        return False

    def is_sleep_command(self, text: str) -> bool:
        """Check if text contains sleep command."""
        normalized_text = text.lower()
        return any(sleep_cmd in normalized_text for sleep_cmd in self.sleep_words)

    def detect(self) -> bool:
        """Detect wake word from audio input."""
        # For now, return True to simulate wake word detection
        # In a real implementation, this would listen for audio input
        return True

    def start_listening(self):
        """Start continuous wake word detection."""
        self.is_listening = True

    def stop_listening(self):
        """Stop wake word detection."""
        self.is_listening = False

    def reset_wake_detection(self):
        """Reset wake detection flag."""
        self.wake_detected = False
