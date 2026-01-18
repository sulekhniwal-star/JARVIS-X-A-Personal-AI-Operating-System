"""
JARVIS - Advanced AI Voice Assistant
=====================================

Features:
- AI-powered intent detection using Gemini
- Advanced context-aware memory system
- Wake word detection ("Hey Jarvis")
- Modern PyQt5 GUI with audio visualization
- Conversation history and learning
- Multi-threaded architecture for smooth operation
"""

import webbrowser
import google.generativeai as genai
import os
import datetime
import pyjokes
import requests
import speech_recognition as sr
import sys
import threading
import sounddevice as sd
import soundfile as sf
import numpy as np
import io

# Enhanced speech recognition
try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False
    print("⚠️ Whisper not available - using Google Speech only")

# System monitoring
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("⚠️ psutil not available - system info disabled")

# Screenshot capability
try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    print("⚠️ pyautogui not available - screenshot disabled")

# Try to import pycaw for audio control
try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    HAS_AUDIO_CONTROL = True
except (ImportError, Exception):
    HAS_AUDIO_CONTROL = False
    print("⚠️  pycaw not available - volume control disabled")

# Try to import pyttsx3 for offline TTS
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

# Try to import gTTS for online TTS (fallback)
try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

# Try to import pygame for audio playback (alternative to playsound)
try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

# Print TTS status
if HAS_PYTTSX3:
    print("✅ pyttsx3 Text-to-Speech enabled (offline)")
elif HAS_GTTS:
    print("✅ Google Text-to-Speech enabled (online)")
else:
    print("⚠️  No TTS available - responses will be text-only")

# Import custom modules
from memory import JarvisMemory
from intent_detector import IntentDetector
from wake_word import WakeWordDetector


class JarvisAssistant:
    """Main JARVIS Assistant class."""
    
    def __init__(self, api_key: str, use_gui: bool = False):
        self.api_key = api_key
        self.use_gui = use_gui
        
        # Initialize core systems
        self.memory = JarvisMemory()
        self.intent_detector = IntentDetector(api_key)
        self.wake_word_detector = WakeWordDetector(on_wake_callback=self.on_wake_word)
        
        # Voice settings - Initialize TTS engine
        self.engine = None
        self.tts_method = None  # 'pyttsx3', 'gtts', or None
        
        if HAS_PYTTSX3:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 150)  # Set speech rate (150 WPM)
                self.tts_method = 'pyttsx3'
            except Exception as e:
                print(f"⚠️  pyttsx3 initialization failed: {e}")
                self.engine = None
        
        # Fallback to gTTS if pyttsx3 not available
        if not self.tts_method and HAS_GTTS:
            self.tts_method = 'gtts'
        
        self.recognizer = sr.Recognizer()
        
        # State
        self.is_running = True
        self.awaiting_command = False
        
        print("✅ JARVIS Initialized Successfully!")
        print(f"📝 User: {self.memory.memory.get('owner', 'Guest')}")
        print(f"📍 Location: {self.memory.memory.get('city', 'Unknown')}")
    
    def speak(self, text: str):
        """Convert text to speech using available TTS engines."""
        try:
            print(f"🔊 JARVIS: {text}")
            
            # Method 1: Use pyttsx3 (offline, fastest)
            if self.tts_method == 'pyttsx3' and self.engine:
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                    return
                except Exception as e:
                    print(f"⚠️  pyttsx3 error: {e}")
            
            # Method 2: Use Google Text-to-Speech (online)
            if self.tts_method == 'gtts' and HAS_GTTS:
                try:
                    # Limit text length to avoid API issues
                    text_to_speak = text[:500] if len(text) > 500 else text
                    
                    # Create TTS object
                    tts = gTTS(text=text_to_speak, lang='en', slow=False)
                    
                    # Save to temporary file
                    temp_audio = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "jarvis_tts.mp3")
                    tts.save(temp_audio)
                    
                    # Use PowerShell to play the audio
                    import subprocess
                    subprocess.Popen(['powershell', '-c', f'(New-Object System.Media.SoundPlayer).SoundLocation=\'{temp_audio}\';(New-Object System.Media.SoundPlayer).PlaySync()'],
                                     creationflags=subprocess.CREATE_NO_WINDOW,
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
                    return
                except Exception as e:
                    print(f"⚠️  gTTS error: {e}")
            
            # Fallback: Just print (no TTS available)
            # Text is already printed above, so just continue
            
        except Exception as e:
            print(f"❌ Speech error: {e}")
    
    def listen_with_sounddevice(self, timeout: int = 5) -> str:
        """Enhanced audio capture with Whisper support."""
        try:
            print("🎤 Listening (enhanced)...")
            sample_rate = 16000
            
            # Record audio
            audio_data = sd.rec(int(sample_rate * timeout), samplerate=sample_rate, channels=1, dtype='float32')
            sd.wait()
            
            print("🔄 Processing...")
            
            # Try Whisper first (best accuracy)
            if HAS_WHISPER:
                try:
                    model = whisper.load_model("base")
                    result = model.transcribe(audio_data.flatten())
                    text = result["text"].strip()
                    if text:
                        print(f"👤 You (Whisper): {text}")
                        return text.lower()
                except Exception as e:
                    print(f"⚠️ Whisper failed: {e}")
            
            # Fallback to Google
            audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
            audio = sr.AudioData(audio_bytes, sample_rate, 2)
            query = self.recognizer.recognize_google(audio, language='en-in')
            print(f"👤 You (Google): {query}")
            return query.lower()
        
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ API Error: {e}")
            return None
        except Exception as e:
            print(f"❌ Speech error: {e}")
            return None

    def listen(self, timeout: int = 5) -> str:
        """Listen for voice input with sounddevice backend (with text fallback)."""
        # Try sounddevice first
        result = self.listen_with_sounddevice(timeout)
        if result is not None:
            return result
        
        # Fallback to text input if sounddevice fails
        print(f"\n⚠️  Microphone unavailable - using TEXT INPUT mode")
        print("="*50)
        try:
            user_input = input("\n💬 Type your command: ").strip()
            if user_input:
                print(f"👤 You: {user_input}")
                return user_input.lower()
        except Exception as input_error:
            print(f"❌ Input error: {input_error}")
        return None
    
    def get_weather(self, location: str):
        """Fetch weather information."""
        try:
            # Geocoding API
            geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
            geocoding_params = {"name": location, "count": 1, "language": "en", "format": "json"}
            geocoding_res = requests.get(geocoding_url, params=geocoding_params, timeout=5)
            geocoding_data = geocoding_res.json()
            
            if "results" not in geocoding_data or len(geocoding_data["results"]) == 0:
                self.speak(f"Sorry, I couldn't find the location: {location}")
                return
            
            location_data = geocoding_data["results"][0]
            latitude = location_data['latitude']
            longitude = location_data['longitude']
            city = location_data['name']
            
            # Weather API
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": "true",
            }
            
            weather_res = requests.get(url, params=params, timeout=5)
            weather_data = weather_res.json()
            
            temperature = weather_data['current_weather']['temperature']
            weather_code = weather_data['current_weather']['weathercode']
            
            # Simple weather description
            weather_desc = self._get_weather_description(weather_code)
            
            response = f"The weather in {city} is {weather_desc} with a temperature of {temperature}°C."
            self.speak(response)
            
            # Store in memory
            self.memory.add_habit(f"weather_check_{city}")
        
        except requests.RequestException:
            self.speak("I couldn't fetch the weather. Please check your internet connection.")
        except Exception as e:
            print(f"❌ Weather error: {e}")
            self.speak("Sorry, I couldn't get the weather information.")
    
    def _get_weather_description(self, code: int) -> str:
        """Convert WMO weather code to description."""
        weather_codes = {
            0: "clear sky",
            1: "mostly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            51: "drizzling",
            61: "rainy",
            71: "snowing",
            80: "rain showers",
            95: "thunderstorm"
        }
        return weather_codes.get(code, "cloudy")
    
    def process_intent(self, intent: str, confidence: float, metadata: dict, user_input: str):
        """Process detected intent and execute action."""
        print(f"🧠 Intent: {intent} (Confidence: {confidence:.2f})")
        
        if intent == 'greeting':
            self.speak("Hello there! How can I assist you today?")
        
        elif intent == 'time':
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.speak(f"The current time is {current_time}")
        
        elif intent == 'joke':
            joke = pyjokes.get_joke()
            self.speak(joke)
        
        elif intent == 'weather':
            location = metadata.get('location')
            if location:
                self.get_weather(location)
            else:
                default_city = self.memory.memory.get('city', 'Indore')
                self.speak(f"Getting weather for {default_city}")
                self.get_weather(default_city)
        
        elif intent == 'open_app':
            app_name = metadata.get('app_name', '').lower()
            self._open_application(app_name)
        
        elif intent == 'volume':
            action = metadata.get('action')
            level = metadata.get('level')
            self._control_volume(action, level)
        
        elif intent == 'system_info':
            info = self.get_system_info()
            if info:
                response = f"System status: CPU {info['cpu_percent']:.1f}%, Memory {info['memory_percent']:.1f}%, Disk {info['disk_percent']:.1f}%"
            else:
                response = "Could not get system information"
            self.speak(response)
        
        elif intent == 'screenshot':
            if not HAS_PYAUTOGUI:
                response = "Screenshot feature not available - pyautogui not installed"
            else:
                try:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshot_{timestamp}.png"
                    pyautogui.screenshot(filename)
                    response = f"Screenshot saved as {filename}"
                except Exception as e:
                    response = "Could not take screenshot"
            self.speak(response)
        
        elif intent == 'shutdown':
            self.speak("Shutting down the system")
            os.system("shutdown /s /t 5")
        
        elif intent == 'exit':
            self.speak("Goodbye! It was a pleasure assisting you.")
            self.is_running = False
        
        elif intent == 'ai_response':
            # Get AI response with context
            context = self.memory.get_context_summary()
            response = self.intent_detector.get_ai_response(user_input, context)
            self.speak(response)
            self.memory.add_conversation(user_input, response, intent)
        
        else:
            self.speak(f"I'm not sure how to handle that request: {intent}")
        
        # Add to memory
        self.memory.add_conversation(user_input, "", intent)
    
    def _open_application(self, app_name: str):
        """Open an application."""
        app_paths = {
            'chrome': "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            'youtube': "https://www.youtube.com",
            'spotify': "https://www.spotify.com",
            'notepad': "C:\\Windows\\notepad.exe",
            'calculator': "C:\\Windows\\System32\\calc.exe",
            'vscode': "C:\\Program Files\\Microsoft VS Code\\Code.exe"
        }
        
        if app_name in app_paths:
            path = app_paths[app_name]
            if path.startswith('http'):
                webbrowser.open(path)
            else:
                try:
                    os.startfile(path)
                except Exception as e:
                    self.speak(f"Could not open {app_name}: {str(e)}")
            self.speak(f"Opening {app_name}")
            self.memory.add_habit(f"opened_{app_name}")
        else:
            self.speak(f"I don't know how to open {app_name}")
    
    def _control_volume(self, action: str = None, level: int = None):
        """Control system volume."""
        if not HAS_AUDIO_CONTROL:
            self.speak("Volume control is not available on this system")
            return
        
        try:
            # Get the audio device and volume interface
            device = AudioUtilities.GetSpeakers()
            volume = device.EndpointVolume
            
            # Get current volume level (0.0 - 1.0)
            current_level = volume.GetMasterVolumeLevelScalar()
            current_percent = int(current_level * 100)
            
            if action == 'mute':
                volume.SetMute(True, None)
                self.speak("Volume muted")
            
            elif action == 'unmute':
                volume.SetMute(False, None)
                self.speak("Volume unmuted")
            
            elif action == 'increase':
                # Increase volume by 10%
                new_level = min(1.0, current_level + 0.1)
                volume.SetMasterVolumeLevelScalar(new_level, None)
                self.speak(f"Volume increased to {int(new_level * 100)} percent")
            
            elif action == 'increase_by' and level:
                # Increase volume by specified amount
                new_level = min(1.0, current_level + (level / 100.0))
                volume.SetMasterVolumeLevelScalar(new_level, None)
                self.speak(f"Volume increased by {level} percent to {int(new_level * 100)} percent")
            
            elif action == 'decrease':
                # Decrease volume by 10%
                new_level = max(0.0, current_level - 0.1)
                volume.SetMasterVolumeLevelScalar(new_level, None)
                self.speak(f"Volume decreased to {int(new_level * 100)} percent")
            
            elif action == 'decrease_by' and level:
                # Decrease volume by specified amount
                new_level = max(0.0, current_level - (level / 100.0))
                volume.SetMasterVolumeLevelScalar(new_level, None)
                self.speak(f"Volume decreased by {level} percent to {int(new_level * 100)} percent")
            
            elif action == 'set' and level is not None:
                if 0 <= level <= 100:
                    volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                    self.speak(f"Volume set to {level} percent")
                else:
                    self.speak("Volume must be between 0 and 100")
            
            else:
                self.speak("Volume action not recognized")
        
        except Exception as e:
            print(f"❌ Volume control error: {type(e).__name__}: {e}")
            self.speak("I couldn't control the volume")
    
    def get_system_info(self) -> Dict[str, any]:
        """Get system information."""
        if not HAS_PSUTIL:
            return {}
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': round((disk.used / disk.total) * 100, 1)
            }
        except Exception as e:
            print(f"❌ System info error: {e}")
            return {}
    
    def on_wake_word(self):
        """Callback when wake word is detected."""
        self.awaiting_command = True
        self.speak("Yes, sir?")
    
    def run_terminal_mode(self):
        """Run JARVIS in terminal mode."""
        self.speak(f"Hello! I'm JARVIS, ready to assist {self.memory.memory.get('owner', 'you')}.")
        
        while self.is_running:
            try:
                print("\n📢 Say 'Hey Jarvis' or type your command:")
                print("(Type 'exit' to quit)\n")
                
                # Listen for wake word
                query = self.listen()
                
                if query is None:
                    continue
                
                # Check for wake word
                if 'jarvis' in query:
                    self.speak("Yes, sir?")
                    command = self.listen()
                    if command:
                        self._process_command(command)
                elif 'exit' in query or 'quit' in query:
                    self.speak("Goodbye!")
                    self.is_running = False
                    break
            
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
                self.is_running = False
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _process_command(self, command: str):
        """Process a command."""
        intent, confidence, metadata = self.intent_detector.detect_intent(command)
        self.process_intent(intent, confidence, metadata, command)
    
    def run_gui_mode(self):
        """Run JARVIS with GUI."""
        try:
            from gui import JarvisGUI, JarvisCore
            
            app_core = JarvisCore(self.memory, self.intent_detector, self.wake_word_detector)
            gui = JarvisGUI(app_core)
            gui.show()
            
            sys.exit(gui.app.exec_())
        except ImportError:
            print("❌ PyQt5 not installed. Falling back to terminal mode.")
            self.run_terminal_mode()
    
    def run(self, use_gui: bool = False):
        """Start JARVIS."""
        print("\n" + "="*60)
        print("🤖 JARVIS - Advanced AI Voice Assistant")
        print("="*60)
        
        if use_gui:
            self.run_gui_mode()
        else:
            self.run_terminal_mode()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='JARVIS - Advanced AI Voice Assistant')
    parser.add_argument('--api-key', type=str, default="YOUR_GEMINI_API_KEY",
                        help='Gemini API Key')
    parser.add_argument('--gui', action='store_true', help='Use GUI mode')
    
    args = parser.parse_args()
    
    # Initialize and run
    jarvis = JarvisAssistant(api_key=args.api_key, use_gui=args.gui)
    jarvis.run(use_gui=args.gui)


if __name__ == '__main__':
    main()