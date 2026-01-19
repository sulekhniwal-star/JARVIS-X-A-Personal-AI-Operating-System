@echo off
echo Installing Enhanced Jarvis dependencies...
pip install -r requirements.txt

echo.
echo Enhanced Jarvis Setup Complete!
echo.
echo IMPORTANT: Edit .env file and add your API keys:
echo - Gemini API key (for AI conversations)
echo - News API key (optional, for news updates)
echo - Spotify keys (optional, for music control)
echo.
echo New Features:
echo - Natural conversations with AI memory
echo - Realistic voice with multiple accents
echo - Cross-platform support (Windows/Mac/Linux)
echo - News updates: "Jarvis, what's the news?"
echo - Reminders: "Jarvis, remind me in 10 minutes to call mom"
echo - Voice selection: "Jarvis, change voice to british"
echo - Robust error handling and offline mode
echo - YouTube, Wikipedia, weather, system control
echo.
echo To run: python jarvis.py
echo.
pause