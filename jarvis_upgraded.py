"""
JARVIS - UPGRADED Advanced AI Voice Assistant
============================================
Major Upgrades:
✅ Enhanced Speech Recognition (Whisper/Vosk/Google)
✅ Advanced NLP Intent Detection with Learning
✅ Intelligent Memory System with SQLite
✅ Powerful System Automation
✅ Natural Voice Output with Emotions
✅ Context-Aware Responses
"""

import os
import sys
import datetime
import threading
import time
from typing import Optional, Dict, Any

# Import enhanced modules
from enhanced_speech import EnhancedSpeechRecognizer, ContinuousListener
from advanced_nlp import AdvancedIntentDetector
from enhanced_memory import EnhancedMemory
from system_automation import SystemAutomation
from enhanced_tts import EnhancedTTS, ContextualSpeaker

# Import existing modules for compatibility
try:
    from gui import JarvisGUI, JarvisCore
    HAS_GUI = True
except ImportError:
    HAS_GUI = False
    print("⚠️ GUI not available")

class UpgradedJarvis:
    """Upgraded JARVIS with enhanced capabilities."""
    
    def __init__(self, api_key: str = "YOUR_GEMINI_API_KEY"):
        print("\n" + "="*60)
        print("🚀 JARVIS UPGRADE - Advanced AI Assistant")
        print("="*60)
        
        self.api_key = api_key
        self.is_running = True
        self.is_listening = False
        
        # Initialize enhanced systems
        print("🔧 Initializing enhanced systems...")
        
        # Core systems
        self.speech_recognizer = EnhancedSpeechRecognizer()
        self.intent_detector = AdvancedIntentDetector(api_key)
        self.memory = EnhancedMemory()
        self.system_automation = SystemAutomation()
        self.tts = EnhancedTTS()
        self.contextual_speaker = ContextualSpeaker(self.tts)
        
        # Continuous listener
        self.continuous_listener = ContinuousListener(
            self.speech_recognizer, 
            self.on_wake_word_detected
        )
        
        # Load user preferences
        self.user_name = self.memory.get_preference('name', 'Sir')
        self.location = self.memory.get_preference('location', 'Indore')
        
        print(f"✅ JARVIS Upgraded Successfully!")
        print(f"👤 User: {self.user_name}")
        print(f"📍 Location: {self.location}")
        print(f"🧠 Memory: Enhanced with learning")
        print(f"🎤 Speech: Multi-engine recognition")
        print(f"🔊 Voice: Emotional TTS")
        print(f"⚙️ System: Advanced automation")
    
    def on_wake_word_detected(self, wake_phrase: str):
        """Handle wake word detection."""
        print(f"👂 Wake word detected: {wake_phrase}")
        self.contextual_speaker.speak_contextual("Yes sir, how can I help you?", "greeting")
        
        # Listen for command
        command = self.speech_recognizer.listen(timeout=8)
        if command:
            self.process_command(command)
        else:
            self.contextual_speaker.speak_contextual("I didn't catch that. Please try again.", "error")
    
    def process_command(self, command: str):
        """Process user command with enhanced intelligence."""
        try:
            # Get context for better understanding
            context = self.memory.get_context_summary()
            
            # Detect intent with AI
            intent, confidence, entities = self.intent_detector.detect_intent(command, context)
            
            print(f"🧠 Intent: {intent} (Confidence: {confidence:.2f})")
            print(f"📊 Entities: {entities}")
            
            # Execute action based on intent
            response = self.execute_intent(intent, entities, command)
            
            # Add to memory
            self.memory.add_conversation(command, response, intent, context)
            
        except Exception as e:
            print(f"❌ Command processing error: {e}")
            self.contextual_speaker.speak_contextual("I encountered an error processing that command.", "error")
    
    def execute_intent(self, intent: str, entities: Dict[str, Any], original_command: str) -> str:
        """Execute the detected intent."""
        
        if intent == 'greeting':
            response = self.handle_greeting()
        
        elif intent == 'time':
            response = self.handle_time_request()
        
        elif intent == 'date':
            response = self.handle_date_request()
        
        elif intent == 'weather':
            location = entities.get('location', self.location)
            response = self.handle_weather_request(location)
        
        elif intent.startswith('open_'):
            app_name = entities.get('app', intent.replace('open_', ''))
            response = self.handle_open_app(app_name)
        
        elif intent in ['volume_up', 'volume_down', 'mute']:
            action = entities.get('action', intent.replace('volume_', ''))
            level = entities.get('level')
            response = self.handle_volume_control(action, level)
        
        elif intent == 'system_info':
            response = self.handle_system_info()
        
        elif intent == 'screenshot':
            response = self.handle_screenshot()
        
        elif intent == 'search':
            query = entities.get('query', original_command.replace('search for', '').strip())
            response = self.handle_search(query)
        
        elif intent == 'reminder':
            reminder_text = entities.get('reminder_text', original_command)
            response = self.handle_reminder(reminder_text)
        
        elif intent == 'joke':
            response = self.handle_joke()
        
        elif intent == 'news':
            response = self.handle_news()
        
        elif intent == 'shutdown':
            response = self.handle_shutdown()
        
        elif intent == 'restart':
            response = self.handle_restart()
        
        elif intent == 'exit':
            response = self.handle_exit()
        
        else:
            # AI-powered response for complex queries
            response = self.handle_ai_response(original_command)
        
        return response
    
    def handle_greeting(self) -> str:
        """Handle greeting with context awareness."""
        current_hour = datetime.datetime.now().hour
        
        if 5 <= current_hour < 12:
            greeting = f"Good morning, {self.user_name}!"
        elif 12 <= current_hour < 17:
            greeting = f"Good afternoon, {self.user_name}!"
        elif 17 <= current_hour < 21:
            greeting = f"Good evening, {self.user_name}!"
        else:
            greeting = f"Hello, {self.user_name}!"
        
        # Add contextual information
        suggestions = self.memory.get_smart_suggestions()
        if suggestions:
            greeting += f" Would you like me to {suggestions[0].lower()}?"
        
        self.contextual_speaker.speak_contextual(greeting, "greeting")
        return greeting
    
    def handle_time_request(self) -> str:
        """Handle time request."""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        response = f"The current time is {current_time}"
        self.contextual_speaker.speak_contextual(response, "time")
        return response
    
    def handle_date_request(self) -> str:
        """Handle date request."""
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        response = f"Today is {current_date}"
        self.contextual_speaker.speak_contextual(response, "time")
        return response
    
    def handle_weather_request(self, location: str) -> str:
        """Handle weather request with enhanced API."""
        try:
            import requests
            
            # Use OpenWeatherMap or similar API
            # For now, using a simple response
            response = f"I'll check the weather for {location}. Weather integration requires API setup."
            self.contextual_speaker.speak_contextual(response, "weather")
            return response
            
        except Exception as e:
            response = "I couldn't fetch the weather information right now."
            self.contextual_speaker.speak_contextual(response, "error")
            return response
    
    def handle_open_app(self, app_name: str) -> str:
        """Handle application opening."""
        success = self.system_automation.open_application(app_name)
        
        if success:
            response = f"Opening {app_name}"
            self.contextual_speaker.speak_contextual(response, "success")
            self.memory.set_preference(f"last_opened_app", app_name)
        else:
            response = f"I couldn't open {app_name}. Please check if it's installed."
            self.contextual_speaker.speak_contextual(response, "error")
        
        return response
    
    def handle_volume_control(self, action: str, level: int = None) -> str:
        """Handle volume control."""
        success = self.system_automation.control_volume(action, level)
        
        if success:
            if action == 'mute':
                response = "Volume muted"
            elif action == 'unmute':
                response = "Volume unmuted"
            elif action == 'set' and level:
                response = f"Volume set to {level} percent"
            elif action == 'increase':
                response = "Volume increased"
            elif action == 'decrease':
                response = "Volume decreased"
            else:
                response = "Volume adjusted"
            
            self.contextual_speaker.speak_contextual(response, "success")
        else:
            response = "I couldn't control the volume"
            self.contextual_speaker.speak_contextual(response, "error")
        
        return response
    
    def handle_system_info(self) -> str:
        """Handle system information request."""
        info = self.system_automation.get_system_info()
        
        if info:
            cpu_usage = info.get('cpu', {}).get('usage_percent', 0)
            memory_usage = info.get('memory', {}).get('usage_percent', 0)
            
            response = f"System status: CPU usage is {cpu_usage:.1f}%, Memory usage is {memory_usage:.1f}%"
            self.contextual_speaker.speak_contextual(response, "system_info")
        else:
            response = "I couldn't retrieve system information"
            self.contextual_speaker.speak_contextual(response, "error")
        
        return response
    
    def handle_screenshot(self) -> str:
        """Handle screenshot request."""
        filename = self.system_automation.take_screenshot()
        
        if filename:
            response = f"Screenshot saved as {os.path.basename(filename)}"
            self.contextual_speaker.speak_contextual(response, "success")
        else:
            response = "I couldn't take a screenshot"
            self.contextual_speaker.speak_contextual(response, "error")
        
        return response
    
    def handle_search(self, query: str) -> str:
        """Handle search request."""
        if query:
            import webbrowser
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            response = f"Searching for {query}"
            self.contextual_speaker.speak_contextual(response, "success")
        else:
            response = "What would you like me to search for?"
            self.contextual_speaker.speak_contextual(response, "neutral")
        
        return response
    
    def handle_reminder(self, reminder_text: str) -> str:
        """Handle reminder creation."""
        try:
            reminder_id = self.memory.add_reminder(reminder_text)
            response = f"I'll remind you about: {reminder_text}"
            self.contextual_speaker.speak_contextual(response, "reminder")
        except Exception as e:
            response = "I couldn't set that reminder"
            self.contextual_speaker.speak_contextual(response, "error")
        
        return response
    
    def handle_joke(self) -> str:
        """Handle joke request."""
        try:
            import pyjokes
            joke = pyjokes.get_joke()
            self.contextual_speaker.speak_contextual(joke, "joke")
            return joke
        except Exception as e:
            response = "I'm not feeling very funny right now"
            self.contextual_speaker.speak_contextual(response, "neutral")
            return response
    
    def handle_news(self) -> str:
        """Handle news request."""
        response = "I'll get the latest news for you. News integration requires API setup."
        self.contextual_speaker.speak_contextual(response, "neutral")
        return response
    
    def handle_shutdown(self) -> str:
        """Handle shutdown request."""
        response = "Shutting down the system in 5 seconds"
        self.contextual_speaker.speak_contextual(response, "warning", "high")
        self.system_automation.system_power("shutdown", 5)
        return response
    
    def handle_restart(self) -> str:
        """Handle restart request."""
        response = "Restarting the system in 5 seconds"
        self.contextual_speaker.speak_contextual(response, "warning", "high")
        self.system_automation.system_power("restart", 5)
        return response
    
    def handle_exit(self) -> str:
        """Handle exit request."""
        response = f"Goodbye, {self.user_name}! It was a pleasure assisting you."
        self.contextual_speaker.speak_contextual(response, "goodbye")
        self.is_running = False
        return response
    
    def handle_ai_response(self, query: str) -> str:
        """Handle complex queries with AI."""
        try:
            context = self.memory.get_context_summary()
            response = self.intent_detector.get_contextual_response("ai_response", {}, query)
            self.contextual_speaker.speak_contextual(response, "neutral")
            return response
        except Exception as e:
            response = "I'm not sure how to help with that"
            self.contextual_speaker.speak_contextual(response, "error")
            return response
    
    def run_terminal_mode(self):
        """Run JARVIS in enhanced terminal mode."""
        self.contextual_speaker.speak_contextual(
            f"Hello {self.user_name}! JARVIS upgraded systems are online and ready.", 
            "greeting"
        )
        
        # Start continuous listening
        self.continuous_listener.start()
        
        try:
            while self.is_running:
                print("\n" + "="*50)
                print("🎤 Say 'Hey Jarvis' or type your command:")
                print("(Type 'exit' to quit)")
                print("="*50)
                
                # Get user input (voice or text)
                user_input = input("\n💬 Type command (or press Enter for voice): ").strip()
                
                if user_input:
                    if user_input.lower() in ['exit', 'quit', 'goodbye']:
                        self.handle_exit()
                        break
                    else:
                        self.process_command(user_input)
                else:
                    # Listen for voice command
                    print("🎤 Listening for voice command...")
                    command = self.speech_recognizer.listen(timeout=5)
                    if command:
                        if 'jarvis' in command.lower():
                            # Extract command after wake word
                            parts = command.lower().split('jarvis', 1)
                            if len(parts) > 1:
                                actual_command = parts[1].strip()
                                if actual_command:
                                    self.process_command(actual_command)
                        else:
                            self.process_command(command)
                
                time.sleep(0.5)  # Brief pause
                
        except KeyboardInterrupt:
            print("\n👋 Shutting down JARVIS...")
        finally:
            self.continuous_listener.stop()
            self.memory.close()
    
    def run_gui_mode(self):
        """Run JARVIS with enhanced GUI."""
        if not HAS_GUI:
            print("❌ GUI not available. Running in terminal mode.")
            self.run_terminal_mode()
            return
        
        try:
            # Create enhanced GUI core
            gui_core = EnhancedJarvisCore(self)
            gui = JarvisGUI(gui_core)
            gui.show()
            
            import sys
            from PyQt5.QtWidgets import QApplication
            app = QApplication.instance() or QApplication(sys.argv)
            sys.exit(app.exec_())
            
        except Exception as e:
            print(f"❌ GUI error: {e}")
            print("Falling back to terminal mode...")
            self.run_terminal_mode()
    
    def run(self, use_gui: bool = False):
        """Start the upgraded JARVIS."""
        if use_gui:
            self.run_gui_mode()
        else:
            self.run_terminal_mode()

class EnhancedJarvisCore:
    """Enhanced core for GUI integration."""
    
    def __init__(self, jarvis_instance: UpgradedJarvis):
        self.jarvis = jarvis_instance
        self.memory = jarvis_instance.memory
        self.intent_detector = jarvis_instance.intent_detector
        self.wake_word_detector = None  # Use continuous listener instead
    
    def listen(self):
        """Listen for voice command."""
        return self.jarvis.speech_recognizer.listen()
    
    def speak(self, text: str):
        """Speak text output."""
        return self.jarvis.tts.speak(text)

def main():
    """Main entry point for upgraded JARVIS."""
    import argparse
    
    parser = argparse.ArgumentParser(description='JARVIS - Upgraded AI Voice Assistant')
    parser.add_argument('--api-key', type=str, default="YOUR_GEMINI_API_KEY",
                        help='Gemini API Key for AI features')
    parser.add_argument('--gui', action='store_true', help='Use GUI mode')
    parser.add_argument('--voice-engine', type=str, default='auto',
                        choices=['auto', 'pyttsx3', 'edge', 'gtts'],
                        help='Preferred TTS engine')
    parser.add_argument('--speech-engine', type=str, default='auto',
                        choices=['auto', 'whisper', 'vosk', 'google'],
                        help='Preferred speech recognition engine')
    
    args = parser.parse_args()
    
    # Initialize and run upgraded JARVIS
    jarvis = UpgradedJarvis(api_key=args.api_key)
    
    # Configure engines if specified
    if args.voice_engine != 'auto':
        jarvis.tts.preferred_engine = args.voice_engine
    
    if args.speech_engine != 'auto':
        jarvis.speech_recognizer.preferred_engine = args.speech_engine
    
    # Run JARVIS
    jarvis.run(use_gui=args.gui)

if __name__ == '__main__':
    main()