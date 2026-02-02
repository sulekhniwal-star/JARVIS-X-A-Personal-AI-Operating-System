from typing import Any
"""Text-to-speech functionality."""

import pyttsx3  # type: ignore
import time
from utils.logger import logger


class TextToSpeech:
    """Handles text-to-speech conversion using pyttsx3."""

    _engine: Any = None

    def __init__(self):
        self.voice_mode = "jarvis"
        self._init_engine()

    @classmethod
    def _init_engine(cls):
        """Initialize the TTS engine once."""
        if cls._engine is None:
            cls._engine = pyttsx3.init()  # type: ignore
            # Set default properties
            cls._engine.setProperty('rate', 180)  # type: ignore  # Words per minute
            cls._engine.setProperty('volume', 0.9)  # type: ignore  # Volume level (0.0 to 1.0)

    def set_voice_mode(self, mode: str):
        """Set voice profile mode."""
        if mode in ["normal", "jarvis"]:
            self.voice_mode = mode
        else:
            logger.warning(f"Unknown voice mode: {mode}. Using jarvis mode.")
            self.voice_mode = "jarvis"

    def speak(self, text: str):
        """
        Convert text to speech.

        Args:
            text (str): The text to speak.
        """
        if not text or not text.strip():
            logger.warning("Empty or None text provided to speak method.")
            return

        try:
            self._init_engine()

            # Apply voice profile settings
            if self.voice_mode == "jarvis":
                # Slower rate (15% slower)
                self._engine.setProperty('rate', 153)  # type: ignore
                # Lower pitch if supported
                try:
                    voices = self._engine.getProperty('voices')  # type: ignore
                    if voices:
                        self._engine.setProperty('voice', voices[0].id)  # type: ignore
                except:
                    pass  # Fail gracefully if pitch control unsupported
                # Pause before speaking
                time.sleep(0.4)
            else:  # normal mode
                self._engine.setProperty('rate', 180)  # type: ignore

            self._engine.say(text)  # type: ignore
            self._engine.runAndWait()  # type: ignore
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
