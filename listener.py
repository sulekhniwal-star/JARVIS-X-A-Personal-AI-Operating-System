import speech_recognition as sr
import threading
from typing import Callable, Optional


class WakeWordDetector:
    """
    Wake word detector for hands-free activation.
    Uses speech recognition to detect "Hey Jarvis" or similar wake words.
    """
    
    WAKE_WORDS = ['jarvis', 'hey jarvis', 'jarvis', 'wake up jarvis']
    
    def __init__(self, on_wake_callback: Optional[Callable] = None):
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.on_wake_callback = on_wake_callback
        self.listen_thread = None
    
    def set_wake_words(self, wake_words: list):
        """Update wake word list."""
        self.WAKE_WORDS = [word.lower() for word in wake_words]
    
    def start(self):
        """Start continuous listening for wake word in background thread."""
        if not self.is_listening:
            self.is_listening = True
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
    
    def stop(self):
        """Stop listening for wake word."""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join()
    
    def _listen_loop(self):
        """Continuous listening loop."""
        with sr.Microphone() as source:
            print("🎤 Wake word detector active. Say 'Hey Jarvis' to activate...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.is_listening:
                try:
                    audio = self.recognizer.listen(source, phrase_time_limit=1.5)
                    text = self.recognizer.recognize_google(audio, language='en-in').lower()
                    
                    for wake_word in self.WAKE_WORDS:
                        if wake_word in text:
                            print(f"✅ Wake word detected! ({text})")
                            if self.on_wake_callback:
                                self.on_wake_callback()
                            break # Exit inner loop once wake word is found
                except sr.UnknownValueError:
                    # This is expected when there is silence
                    pass
                except sr.RequestError as e:
                    print(f"⚠️ Could not request results from Google Speech Recognition service; {e}")
                except Exception as e:
                    print(f"An unexpected error occurred in wake word listener: {e}")
    
    def listen_for_command(self, timeout: int = 5) -> Optional[str]:
        """Listen for a command after wake word activation."""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                print("🎤 Listening for your command...")
                audio = self.recognizer.listen(source, timeout=timeout)
                command = self.recognizer.recognize_google(audio, language='en-in').lower()
                print(f"Command: {command}")
                return command
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Error: {e}")
                return None
            except sr.WaitTimeoutError:
                print("No command heard")
                return None
