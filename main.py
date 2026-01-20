"""Main entry point for Jarvis assistant."""

import sys
from core.config import validate_config
from core.assistant import JarvisAssistant
from face_login import FaceLogin
from voice_login import VoiceLogin

def main():
    try:
        # Validate configuration
        if not validate_config():
            print("Configuration validation failed. Exiting.")
            sys.exit(1)
        
        # Face authentication
        face_login = FaceLogin()
        if not face_login.authenticate():
            print("Access denied.")
            sys.exit(1)
        
        # Voice authentication
        voice_login = VoiceLogin()
        if not voice_login.authenticate():
            print("Voice authentication failed.")
            sys.exit(1)
        
        print("Welcome back, Sulekh.")
        
        # Print startup banner
        print("=" * 50)
        print("           JARVIS ASSISTANT")
        print("=" * 50)
        print("Initializing...")
        
        # Initialize and run assistant
        assistant = JarvisAssistant()
        assistant.run()
        
    except KeyboardInterrupt:
        print("\nShutting down Jarvis. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()