"""Enhanced main entry point for JARVIS-X assistant with multiple free APIs."""

import sys
import os
from pathlib import Path
from loguru import logger

from config import validate_config
from core.assistant import JarvisAssistant
from face_login import FaceLogin
from voice_login import VoiceLogin

def print_startup_banner():
    """Print enhanced startup banner."""
    print("\n" + "=" * 70)
    print("           🤖 JARVIS-X - ENHANCED AI ASSISTANT")
    print("              Your Personal AI Operating System")
    print("=" * 70)
    print("🚀 Features: Entertainment | Information | Productivity | System Control")
    print("🌐 APIs: Weather | News | Crypto | Jokes | Facts | NASA | GitHub")
    print("📱 Free APIs: 15+ integrated services with generous free tiers")
    print("=" * 70)
    print()

def check_environment():
    """Check if environment is properly configured."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("   Run 'python setup.py' to configure JARVIS-X")
        print("   Or copy .env.template to .env and add your API keys")
        return False
    return True

def show_quick_start():
    """Show quick start guide."""
    print("🎯 Quick Start Examples:")
    print("   • 'Tell me a joke' - Get random jokes")
    print("   • 'Weather in London' - Get weather info")
    print("   • 'Latest tech news' - Get current headlines")
    print("   • 'Bitcoin price' - Get crypto prices")
    print("   • 'Add task: Buy groceries' - Create tasks")
    print("   • 'Remind me in 1 hour' - Set reminders")
    print("   • 'What time is it?' - Get current time")
    print("   • 'Help' - See all available commands")
    print()

def handle_environment():
    if not check_environment():
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            print("Run 'python setup.py' to set up JARVIS-X properly.")
            sys.exit(1)

def handle_config_validation():
    print("🔧 Validating configuration...")
    try:
        validate_config()
        print("✅ Configuration validated successfully!")
    except ValueError as e:
        print(f"⚠️  Configuration validation failed: {e}")
        print("   JARVIS will run with limited features.")
        print("   Add GEMINI_API_KEY to .env for full functionality.")

def handle_authentication():
    auth_enabled = os.getenv("ENABLE_FACE_AUTH", "false").lower() == "true"
    if auth_enabled:
        print("\n🔐 Starting authentication...")
        # Face authentication
        try:
            face_login = FaceLogin()
            if not face_login.authenticate():
                print("❌ Face authentication failed.")
                response = input("Continue without face auth? (y/N): ").lower()
                if response != 'y':
                    sys.exit(1)
            else:
                print("✅ Face authentication successful!")
        except (ImportError, OSError, ValueError) as e:
            print(f"⚠️  Face authentication error: {e}")
            print("   Continuing without face authentication...")
        # Voice authentication
        try:
            voice_login = VoiceLogin()
            if not voice_login.authenticate():
                print("❌ Voice authentication failed.")
                response = input("Continue without voice auth? (y/N): ").lower()
                if response != 'y':
                    sys.exit(1)
            else:
                print("✅ Voice authentication successful!")
        except (ImportError, OSError, ValueError) as e:
            print(f"⚠️  Voice authentication error: {e}")
            print("   Continuing without voice authentication...")
    return auth_enabled

def initialize_and_run_assistant(auth_enabled):
    print("\n🎉 Welcome to JARVIS-X Enhanced!")
    print("   Authentication:", "Enabled" if auth_enabled else "Disabled (Development Mode)")
    # Show available features
    show_quick_start()
    print("🚀 Initializing JARVIS-X...")
    print("   Loading AI models...")
    print("   Connecting to APIs...")
    print("   Starting voice recognition...")
    print()
    # Initialize and run assistant
    assistant = JarvisAssistant()
    print("✅ JARVIS-X is ready!")
    print("   Say 'Jarvis' to wake me up, or type your commands.")
    print("   Type 'quit' or 'exit' to shutdown.")
    print("   Type 'help' to see all available commands.")
    print("\n" + "=" * 50)
    assistant.run()

def main():
    """Enhanced main function with better error handling and features showcase."""
    try:
        print_startup_banner()
        handle_environment()
        handle_config_validation()
        auth_enabled = handle_authentication()
        initialize_and_run_assistant(auth_enabled)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down JARVIS-X. Goodbye!")
        logger.info("JARVIS-X shutdown by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        logger.error(f"Critical error in main: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Check your .env file configuration")
        print("   2. Ensure all dependencies are installed")
        print("   3. Run 'python setup.py' to reconfigure")
        print("   4. Check the logs for detailed error information")
        sys.exit(1)

if __name__ == "__main__":
    # Set up logging
    logger.add("logs/jarvis.log", rotation="1 day", retention="7 days")
    logger.info("Starting JARVIS-X Enhanced")

    main()
