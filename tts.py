"""
Enhanced Text-to-Speech System
==============================
Upgrade 5: Natural Voice Output
- Multiple TTS engines (pyttsx3, Edge TTS, gTTS)
- Emotion and tone control
- Voice customization
- Offline and online options
"""

import pyttsx3
import asyncio
import edge_tts
import os
import tempfile
import pygame
from gtts import gTTS
from typing import Optional, Dict, Any
import threading
import time

class EnhancedTTS:
    """Advanced Text-to-Speech with multiple engines and emotion control."""
    
    def __init__(self, preferred_engine: str = "auto"):
        self.preferred_engine = preferred_engine
        self.engines = {}
        self.voice_settings = {
            'rate': 150,
            'volume': 0.9,
            'voice_id': 0,
            'emotion': 'neutral'
        }
        
        # Initialize available engines
        self._init_pyttsx3()
        self._init_pygame()
        
        # Voice profiles for different emotions/contexts
        self.voice_profiles = {
            'neutral': {'rate': 150, 'volume': 0.9},
            'excited': {'rate': 180, 'volume': 1.0},
            'calm': {'rate': 120, 'volume': 0.8},
            'urgent': {'rate': 200, 'volume': 1.0},
            'whisper': {'rate': 100, 'volume': 0.6},
            'announcement': {'rate': 140, 'volume': 1.0}
        }
        
        print(f"✅ Enhanced TTS initialized")
        print(f"🔊 Available engines: {list(self.engines.keys())}")
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 engine."""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            self.engines['pyttsx3'] = {
                'engine': engine,
                'voices': voices,
                'available': True
            }
            
            # Set default voice properties
            engine.setProperty('rate', self.voice_settings['rate'])
            engine.setProperty('volume', self.voice_settings['volume'])
            
            print(f"✅ pyttsx3 engine loaded with {len(voices)} voices")
            
        except Exception as e:
            print(f"⚠️ pyttsx3 initialization failed: {e}")
            self.engines['pyttsx3'] = {'available': False}
    
    def _init_pygame(self):
        """Initialize pygame for audio playback."""
        try:
            pygame.mixer.init()
            self.engines['pygame'] = {'available': True}
            print("✅ pygame audio system initialized")
        except Exception as e:
            print(f"⚠️ pygame initialization failed: {e}")
            self.engines['pygame'] = {'available': False}
    
    def speak(self, text: str, emotion: str = "neutral", engine: str = "auto", 
             rate: int = None, volume: float = None) -> bool:
        """Speak text with specified emotion and settings."""
        
        if not text.strip():
            return False
        
        print(f"🔊 JARVIS ({emotion}): {text}")
        
        # Apply emotion profile
        if emotion in self.voice_profiles:
            profile = self.voice_profiles[emotion]
            actual_rate = rate or profile['rate']
            actual_volume = volume or profile['volume']
        else:
            actual_rate = rate or self.voice_settings['rate']
            actual_volume = volume or self.voice_settings['volume']
        
        # Choose engine
        if engine == "auto":
            engine = self._get_best_engine()
        
        # Speak with selected engine
        if engine == "pyttsx3":
            return self._speak_pyttsx3(text, actual_rate, actual_volume)
        elif engine == "edge":
            return self._speak_edge_tts(text, emotion)
        elif engine == "gtts":
            return self._speak_gtts(text)
        else:
            return self._speak_pyttsx3(text, actual_rate, actual_volume)
    
    def _speak_pyttsx3(self, text: str, rate: int, volume: float) -> bool:
        """Speak using pyttsx3 engine."""
        try:
            if not self.engines.get('pyttsx3', {}).get('available'):
                return False
            
            engine = self.engines['pyttsx3']['engine']
            
            # Set properties
            engine.setProperty('rate', rate)
            engine.setProperty('volume', volume)
            
            # Speak
            engine.say(text)
            engine.runAndWait()
            return True
            
        except Exception as e:
            print(f"❌ pyttsx3 speak error: {e}")
            return False
    
    def _speak_edge_tts(self, text: str, emotion: str = "neutral") -> bool:
        """Speak using Edge TTS (online, high quality)."""
        try:
            # Voice selection based on emotion
            voice_map = {
                'neutral': 'en-US-AriaNeural',
                'excited': 'en-US-JennyNeural',
                'calm': 'en-US-GuyNeural',
                'urgent': 'en-US-AriaNeural',
                'whisper': 'en-US-AriaNeural',
                'announcement': 'en-US-DavisNeural'
            }
            
            voice = voice_map.get(emotion, 'en-US-AriaNeural')
            
            # Run async TTS
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._async_edge_tts(text, voice))
            loop.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Edge TTS error: {e}")
            return False
    
    async def _async_edge_tts(self, text: str, voice: str):
        """Async Edge TTS generation and playback."""
        try:
            # Generate speech
            communicate = edge_tts.Communicate(text, voice)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_path = tmp_file.name
                await communicate.save(tmp_path)
            
            # Play audio
            if self.engines.get('pygame', {}).get('available'):
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
            
            # Clean up
            os.unlink(tmp_path)
            
        except Exception as e:
            print(f"❌ Async Edge TTS error: {e}")
    
    def _speak_gtts(self, text: str) -> bool:
        """Speak using Google TTS."""
        try:
            # Limit text length
            if len(text) > 500:
                text = text[:500] + "..."
            
            # Generate TTS
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_path = tmp_file.name
                tts.save(tmp_path)
            
            # Play audio
            if self.engines.get('pygame', {}).get('available'):
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            
            # Clean up
            os.unlink(tmp_path)
            return True
            
        except Exception as e:
            print(f"❌ gTTS error: {e}")
            return False
    
    def _get_best_engine(self) -> str:
        """Get the best available TTS engine."""
        # Priority: pyttsx3 (offline, fast) > Edge TTS (online, quality) > gTTS (online, backup)
        if self.engines.get('pyttsx3', {}).get('available'):
            return 'pyttsx3'
        else:
            return 'gtts'  # Fallback to gTTS
    
    def set_voice(self, voice_id: int = None, gender: str = None):
        """Set voice by ID or gender preference."""
        try:
            if not self.engines.get('pyttsx3', {}).get('available'):
                return False
            
            engine = self.engines['pyttsx3']['engine']
            voices = self.engines['pyttsx3']['voices']
            
            if voice_id is not None and 0 <= voice_id < len(voices):
                engine.setProperty('voice', voices[voice_id].id)
                self.voice_settings['voice_id'] = voice_id
                return True
            
            elif gender:
                # Find voice by gender
                for i, voice in enumerate(voices):
                    if gender.lower() in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        self.voice_settings['voice_id'] = i
                        return True
            
            return False
            
        except Exception as e:
            print(f"❌ Voice setting error: {e}")
            return False
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices."""
        voices_info = []
        
        try:
            if self.engines.get('pyttsx3', {}).get('available'):
                voices = self.engines['pyttsx3']['voices']
                for i, voice in enumerate(voices):
                    voices_info.append({
                        'id': i,
                        'name': voice.name,
                        'gender': 'female' if 'female' in voice.name.lower() else 'male',
                        'engine': 'pyttsx3'
                    })
        except Exception as e:
            print(f"❌ Voice list error: {e}")
        
        return voices_info
    
    def speak_with_ssml(self, ssml_text: str) -> bool:
        """Speak with SSML markup for advanced control."""
        try:
            # This would work with Edge TTS
            return self._speak_edge_tts(ssml_text)
        except Exception as e:
            print(f"❌ SSML speak error: {e}")
            # Fallback to plain text
            import re
            plain_text = re.sub(r'<[^>]+>', '', ssml_text)
            return self.speak(plain_text)
    
    def speak_async(self, text: str, emotion: str = "neutral", callback: callable = None):
        """Speak asynchronously without blocking."""
        def speak_thread():
            success = self.speak(text, emotion)
            if callback:
                callback(success)
        
        thread = threading.Thread(target=speak_thread, daemon=True)
        thread.start()
        return thread
    
    def stop_speaking(self):
        """Stop current speech."""
        try:
            if self.engines.get('pyttsx3', {}).get('available'):
                engine = self.engines['pyttsx3']['engine']
                engine.stop()
            
            if self.engines.get('pygame', {}).get('available'):
                pygame.mixer.music.stop()
                
        except Exception as e:
            print(f"❌ Stop speaking error: {e}")
    
    def adjust_settings(self, rate: int = None, volume: float = None, voice_id: int = None):
        """Adjust TTS settings."""
        if rate is not None:
            self.voice_settings['rate'] = max(50, min(300, rate))
        
        if volume is not None:
            self.voice_settings['volume'] = max(0.0, min(1.0, volume))
        
        if voice_id is not None:
            self.set_voice(voice_id)
        
        # Apply to pyttsx3 engine
        try:
            if self.engines.get('pyttsx3', {}).get('available'):
                engine = self.engines['pyttsx3']['engine']
                engine.setProperty('rate', self.voice_settings['rate'])
                engine.setProperty('volume', self.voice_settings['volume'])
        except Exception as e:
            print(f"❌ Settings adjustment error: {e}")

# Contextual speaking helper
class ContextualSpeaker:
    """Helper class for context-aware speaking."""
    
    def __init__(self, tts_engine: EnhancedTTS):
        self.tts = tts_engine
        self.context_emotions = {
            'greeting': 'neutral',
            'time': 'neutral',
            'weather': 'neutral',
            'joke': 'excited',
            'error': 'calm',
            'success': 'excited',
            'warning': 'urgent',
            'goodbye': 'calm',
            'system_info': 'neutral',
            'reminder': 'announcement'
        }
    
    def speak_contextual(self, text: str, intent: str = "neutral", urgency: str = "normal"):
        """Speak with context-appropriate emotion."""
        
        # Determine emotion based on intent
        emotion = self.context_emotions.get(intent, 'neutral')
        
        # Adjust for urgency
        if urgency == "high":
            emotion = 'urgent'
        elif urgency == "low":
            emotion = 'whisper'
        
        return self.tts.speak(text, emotion=emotion)