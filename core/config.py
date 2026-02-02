"""Enhanced configuration settings for the JARVIS AI assistant."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Core API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Optional fallback
NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # Free from newsapi.org
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # Free from openweathermap.org
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Email Configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Assistant configuration
ASSISTANT_NAME = "Jarvis"
WAKE_WORD = "jarvis"
DEFAULT_LANGUAGE = "en"
LOG_LEVEL = "INFO"

# Free API Endpoints
FREE_APIS = {
    "quotes": "https://api.quotable.io/random",
    "jokes": "https://official-joke-api.appspot.com/random_joke",
    "facts": "https://uselessfacts.jsph.pl/random.json?language=en",
    "advice": "https://api.adviceslip.com/advice",
    "crypto": "https://api.coingecko.com/api/v3/simple/price",
    "exchange": "https://api.exchangerate-api.com/v4/latest/USD",
    "ip_info": "https://ipapi.co/json/",
    "qr_code": "https://api.qrserver.com/v1/create-qr-code/",
    "cat_facts": "https://catfact.ninja/fact",
    "dog_images": "https://dog.ceo/api/breeds/image/random",
    "nasa_apod": "https://api.nasa.gov/planetary/apod",
    "github": "https://api.github.com",
    "dictionary": "https://api.dictionaryapi.dev/api/v2/entries/en"
}

def validate_config():
    """Validate that required configuration is set."""
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set. Some features may be limited.")
        return False
    return True
