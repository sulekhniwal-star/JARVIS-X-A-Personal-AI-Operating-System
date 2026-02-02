"""Configuration settings for the JARVIS AI assistant."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Key read from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Assistant configuration
ASSISTANT_NAME = "Jarvis"
WAKE_WORD = "jarvis"
DEFAULT_LANGUAGE = "en"
LOG_LEVEL = "INFO"

def validate_config():
    """Validate that required configuration is set."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    return True
