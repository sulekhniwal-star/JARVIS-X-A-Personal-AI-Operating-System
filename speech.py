"""
Enhanced Speech Recognition with Whisper and Vosk support
========================================================
Upgrade 1: Better Speech Recognition
- Whisper (OpenAI) for high accuracy
- Vosk for offline fast recognition
- Fallback to Google Speech Recognition
"""

import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
import numpy as np
import io
import threading
from typing import Optional, Callable
import os

# Try importing Whisper
try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

# Try importing Vosk
try:
    import vosk
    import json
    HAS_VOSK = True
except ImportError:
    HAS_VOSK = False

class EnhancedSpeechRecognizer:
    """Enhanced speech recognition with multiple engines."""
    
    def __init__(self, preferred_engine: str = "auto"):
        self.recognizer = sr.Recognizer()
        self.preferred_engine = preferred_engine
        self.whisper_model = None
        self.vosk_model = None
        
        # Initialize engines
        self._init_whisper()
        self._init_vosk()
        
        print(f"✅ Speech engines available: Whisper={HAS_WHISPER}, Vosk={HAS_VOSK}, Google=True")
    
    def _init_whisper(self):
        """Initialize Whisper model."""
        if HAS_WHISPER:
            try:
                self.whisper_model = whisper.load_model("base")
                print("✅ Whisper model loaded (base)")
            except Exception as e:
                print(f"⚠️ Whisper init failed: {e}")
    
    def _init_vosk(self):
        """Initialize Vosk model."""
        if HAS_VOSK:
            try:
                # Download model if not exists
                model_path = "vosk-model-en-us-0.22"
                if not os.path.exists(model_path):
                    print("⚠️ Vosk model not found. Download from https://alphacephei.com/vosk/models")
                    return
                
                self.vosk_model = vosk.Model(model_path)
                print("✅ Vosk model loaded")
            except Exception as e:
                print(f"⚠️ Vosk init failed: {e}")
    
    def listen(self, timeout: int = 5, engine: str = "auto") -> Optional[str]:
        """Listen with best available engine."""
        if engine == "auto":
            engine = self._get_best_engine()
        
        try:
            # Record audio
            audio_data = self._record_audio(timeout)
            if audio_data is None:
                return None
            
            # Process with selected engine
            if engine == "whisper" and self.whisper_model:
                return self._whisper_recognize(audio_data)
            elif engine == "vosk" and self.vosk_model:
                return self._vosk_recognize(audio_data)
            else:
                return self._google_recognize(audio_data)
                
        except Exception as e:
            print(f"❌ Speech recognition error: {e}")
            return None
    
    def _record_audio(self, timeout: int) -> Optional[np.ndarray]:
        """Record audio using sounddevice."""
        try:
            print("🎤 Listening...")
            sample_rate = 16000
            audio_data = sd.rec(int(sample_rate * timeout), 
                              samplerate=sample_rate, 
                              channels=1, 
                              dtype='float32')
            sd.wait()
            return audio_data.flatten()
        except Exception as e:
            print(f"❌ Audio recording error: {e}")
            return None
    
    def _whisper_recognize(self, audio_data: np.ndarray) -> Optional[str]:
        """Recognize using Whisper."""
        try:
            result = self.whisper_model.transcribe(audio_data)
            text = result["text"].strip()
            if text:
                print(f"👤 You (Whisper): {text}")
                return text.lower()
        except Exception as e:
            print(f"❌ Whisper error: {e}")
        return None
    
    def _vosk_recognize(self, audio_data: np.ndarray) -> Optional[str]:
        """Recognize using Vosk."""
        try:
            rec = vosk.KaldiRecognizer(self.vosk_model, 16000)
            
            # Convert to bytes
            audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
            
            if rec.AcceptWaveform(audio_bytes):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    print(f"👤 You (Vosk): {text}")
                    return text.lower()
        except Exception as e:
            print(f"❌ Vosk error: {e}")
        return None
    
    def _google_recognize(self, audio_data: np.ndarray) -> Optional[str]:
        """Recognize using Google Speech Recognition."""
        try:
            # Convert to AudioData format
            audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
            audio = sr.AudioData(audio_bytes, 16000, 2)
            
            text = self.recognizer.recognize_google(audio, language='en-in')
            print(f"👤 You (Google): {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
        except sr.RequestError as e:
            print(f"❌ Google API error: {e}")
        return None
    
    def _get_best_engine(self) -> str:
        """Get best available engine."""
        if HAS_WHISPER and self.whisper_model:
            return "whisper"
        elif HAS_VOSK and self.vosk_model:
            return "vosk"
        else:
            return "google"

class ContinuousListener:
    """Continuous listening with voice activity detection."""
    
    def __init__(self, speech_recognizer: EnhancedSpeechRecognizer, 
                 wake_callback: Callable[[str], None]):
        self.speech_recognizer = speech_recognizer
        self.wake_callback = wake_callback
        self.is_listening = False
        self.listen_thread = None
    
    def start(self):
        """Start continuous listening."""
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        print("🎤 Continuous listening started")
    
    def stop(self):
        """Stop continuous listening."""
        self.is_listening = False
        print("🔇 Continuous listening stopped")
    
    def _listen_loop(self):
        """Main listening loop."""
        while self.is_listening:
            try:
                # Listen for 3 seconds at a time
                command = self.speech_recognizer.listen(timeout=3)
                if command and self._contains_wake_word(command):
                    self.wake_callback(command)
            except Exception as e:
                print(f"❌ Listening loop error: {e}")
    
    def _contains_wake_word(self, text: str) -> bool:
        """Check if text contains wake word."""
        wake_words = ['jarvis', 'hey jarvis', 'wake up jarvis']
        return any(wake in text.lower() for wake in wake_words)