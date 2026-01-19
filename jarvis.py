import speech_recognition as sr
import edge_tts
import asyncio
import pygame
import io
import datetime
import webbrowser
import os
import requests
import json
import re
import pywhatkit
import wikipedia
import pyautogui
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import google.generativeai as genai
import threading
import time
import logging
import platform
import subprocess
from collections import deque

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Jarvis:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.wake_word = "jarvis"
        self.listening = True
        self.conversation_memory = deque(maxlen=10)
        self.current_voice = "en-US-AriaNeural"
        self.offline_mode = False
        
        # Initialize Gemini AI with error handling
        try:
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            self.model = genai.GenerativeModel('gemini-pro')
            logging.info("Gemini AI initialized")
        except Exception as e:
            logging.error(f"Gemini AI failed: {e}")
            self.model = None
        
        # Initialize pygame for audio
        try:
            pygame.mixer.init()
        except Exception as e:
            logging.error(f"Audio init failed: {e}")
        
        # Initialize Spotify
        self.spotify = None
        try:
            if os.getenv('SPOTIFY_CLIENT_ID'):
                self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
                    redirect_uri="http://localhost:8080",
                    scope="user-modify-playback-state user-read-playback-state"
                ))
        except Exception as e:
            logging.error(f"Spotify init failed: {e}")
        
        # Available voices
        self.voices = {
            "male": "en-US-DavisNeural",
            "female": "en-US-AriaNeural",
            "british": "en-GB-RyanNeural"
        }
        
    async def speak(self, text):
        print(f"Jarvis: {text}")
        
        try:
            communicate = edge_tts.Communicate(text, self.current_voice)
            
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            pygame.mixer.music.load(io.BytesIO(audio_data))
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
        except Exception as e:
            logging.error(f"Speech failed: {e}")
            print(f"Jarvis: {text}")
    
    def listen(self):
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
            
            command = self.recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            logging.error(f"Speech recognition error: {e}")
            self.offline_mode = True
            return ""
        except Exception as e:
            logging.error(f"Listen error: {e}")
            return ""
    
    def get_time(self):
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}"
    
    def get_date(self):
        today = datetime.date.today()
        return f"Today is {today.strftime('%A, %B %d, %Y')}"
    
    def search_web(self, query):
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching for {query}"
    
    def play_youtube(self, query):
        try:
            pywhatkit.playonyt(query)
            return f"Playing {query} on YouTube"
        except:
            return "Couldn't play video"
    
    def get_wikipedia_summary(self, query):
        try:
            summary = wikipedia.summary(query, sentences=2)
            return summary
        except:
            return f"Couldn't find information about {query}"
    
    def control_spotify(self, command):
        if not self.spotify:
            return "Spotify not configured"
        
        try:
            if "play" in command:
                self.spotify.start_playback()
                return "Playing music"
            elif "pause" in command or "stop" in command:
                self.spotify.pause_playback()
                return "Music paused"
            elif "next" in command:
                self.spotify.next_track()
                return "Next song"
            elif "previous" in command:
                self.spotify.previous_track()
                return "Previous song"
        except:
            return "Spotify control failed"
    
    def system_control(self, command):
        try:
            system = platform.system().lower()
            
            if "volume up" in command:
                if system == "windows":
                    pyautogui.press('volumeup')
                elif system == "darwin":
                    subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
                elif system == "linux":
                    subprocess.run(["amixer", "set", "Master", "5%+"])
                return "Volume increased"
                
            elif "volume down" in command:
                if system == "windows":
                    pyautogui.press('volumedown')
                elif system == "darwin":
                    subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
                elif system == "linux":
                    subprocess.run(["amixer", "set", "Master", "5%-"])
                return "Volume decreased"
                
            elif "mute" in command:
                if system == "windows":
                    pyautogui.press('volumemute')
                elif system == "darwin":
                    subprocess.run(["osascript", "-e", "set volume with output muted"])
                elif system == "linux":
                    subprocess.run(["amixer", "set", "Master", "toggle"])
                return "Audio muted"
                
            elif "lock screen" in command:
                if system == "windows":
                    os.system("rundll32.exe user32.dll,LockWorkStation")
                elif system == "darwin":
                    subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
                elif system == "linux":
                    subprocess.run(["xdg-screensaver", "lock"])
                return "Screen locked"
                
            elif "screenshot" in command:
                pyautogui.screenshot("screenshot.png")
                return "Screenshot saved"
                
        except Exception as e:
            logging.error(f"System control error: {e}")
            return "System command failed"
        
        return "System command not recognized"
    
    async def ask_ai(self, question):
        if not self.model:
            return "AI service unavailable"
            
        try:
            context = "\n".join([f"User: {q}\nJarvis: {a}" for q, a in self.conversation_memory])
            full_prompt = f"{context}\nUser: {question}\nJarvis:" if context else question
            
            response = self.model.generate_content(full_prompt)
            self.conversation_memory.append((question, response.text))
            
            return response.text
        except Exception as e:
            logging.error(f"AI error: {e}")
            return "I'm having trouble with my AI brain right now"
    
    def wait_for_wake_word(self):
        # Simple wake word detection using speech recognition
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
            
            command = self.recognizer.recognize_google(audio).lower()
            return self.wake_word in command
        except:
            return False
    
    def get_weather(self, command):
        if self.offline_mode:
            return "Weather requires internet connection"
            
        city_match = re.search(r'weather in (.+)', command)
        city = city_match.group(1) if city_match else "New York"
        
        try:
            url = f"http://wttr.in/{city}?format=%C+%t+in+%l"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                weather_info = response.text.strip()
                return f"The weather is {weather_info}"
            else:
                return f"Sorry, I couldn't get weather for {city}"
        except Exception as e:
            logging.error(f"Weather error: {e}")
            return "Weather service unavailable"
    
    def get_news(self):
        if self.offline_mode:
            return "News requires internet connection"
            
        try:
            url = "https://newsapi.org/v2/top-headlines?country=us&pageSize=3&apiKey=" + os.getenv('NEWS_API_KEY', 'demo')
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                headlines = [article['title'] for article in data.get('articles', [])[:3]]
                return "Top headlines: " + ". ".join(headlines)
            else:
                return "News unavailable"
        except Exception as e:
            logging.error(f"News error: {e}")
            return "Couldn't fetch news"
    
    def set_reminder(self, command):
        time_match = re.search(r'remind me in (\d+) (minutes?|hours?)', command)
        if time_match:
            duration = int(time_match.group(1))
            unit = time_match.group(2)
            message = command.split('to ')[-1] if 'to ' in command else "reminder"
            
            seconds = duration * 60 if 'minute' in unit else duration * 3600
            threading.Timer(seconds, self._reminder_callback, args=[message]).start()
            return f"Reminder set for {duration} {unit}"
        return "Please specify time like 'remind me in 5 minutes to call mom'"
    
    def _reminder_callback(self, message):
        asyncio.create_task(self.speak(f"Reminder: {message}"))
    
    def change_voice(self, command):
        for voice_name, voice_id in self.voices.items():
            if voice_name in command:
                self.current_voice = voice_id
                return f"Voice changed to {voice_name}"
        return "Available voices: male, female, british"
    
    async def process_command(self, command):
        if not command:
            return
            
        try:
            if "time" in command:
                await self.speak(self.get_time())
            elif "date" in command:
                await self.speak(self.get_date())
            elif "weather" in command:
                result = self.get_weather(command)
                await self.speak(result)
            elif "news" in command:
                result = self.get_news()
                await self.speak(result)
            elif "remind me" in command:
                result = self.set_reminder(command)
                await self.speak(result)
            elif "change voice" in command or "voice" in command:
                result = self.change_voice(command)
                await self.speak(result)
            elif "play" in command and "youtube" in command:
                query = command.replace("play", "").replace("youtube", "").strip()
                await self.speak(self.play_youtube(query))
            elif "search" in command:
                query = command.replace("search", "").strip()
                await self.speak(self.search_web(query))
            elif "what is" in command or "who is" in command:
                query = command.replace("what is", "").replace("who is", "").strip()
                result = self.get_wikipedia_summary(query)
                await self.speak(result)
            elif "spotify" in command or "music" in command:
                result = self.control_spotify(command)
                await self.speak(result)
            elif "open" in command:
                await self._handle_open_command(command)
            elif any(word in command for word in ["volume", "mute", "lock", "screenshot"]):
                result = self.system_control(command)
                await self.speak(result)
            elif "shutdown" in command or "exit" in command:
                await self.speak("Goodbye sir. Shutting down.")
                self.listening = False
            elif "hello" in command or "hi" in command:
                await self.speak("Hello sir. How can I assist you today?")
            else:
                if not self.offline_mode:
                    await self.speak("Let me think about that...")
                    ai_response = await self.ask_ai(command)
                    await self.speak(ai_response)
                else:
                    await self.speak("I'm in offline mode. Try basic commands like time, volume, or screenshot.")
                    
        except Exception as e:
            logging.error(f"Command error: {e}")
            await self.speak("Sorry, I encountered an error.")
    
    async def _handle_open_command(self, command):
        try:
            if "notepad" in command:
                if platform.system() == "Windows":
                    os.system("notepad")
                elif platform.system() == "Darwin":
                    os.system("open -a TextEdit")
                else:
                    os.system("gedit")
                await self.speak("Opening text editor")
            elif "calculator" in command:
                if platform.system() == "Windows":
                    os.system("calc")
                elif platform.system() == "Darwin":
                    os.system("open -a Calculator")
                else:
                    os.system("gnome-calculator")
                await self.speak("Opening Calculator")
            elif "browser" in command:
                webbrowser.open("https://www.google.com")
                await self.speak("Opening browser")
        except Exception as e:
            logging.error(f"Open command error: {e}")
            await self.speak("Couldn't open that application")
    
    async def run(self):
        await self.speak("Enhanced Jarvis online. I'm ready for natural conversation.")
        
        while self.listening:
            try:
                if self.wait_for_wake_word():
                    await self.speak("Yes sir?")
                    
                    command = self.listen()
                    if command:
                        command = command.replace(self.wake_word, "").strip()
                        await self.process_command(command)
                
            except KeyboardInterrupt:
                await self.speak("Goodbye sir.")
                break
            except Exception as e:
                logging.error(f"Main loop error: {e}")
                await asyncio.sleep(1)
                if not self.offline_mode:
                    await self.speak("I encountered an error but I'm still here.")

async def main():
    jarvis = Jarvis()
    await jarvis.run()

if __name__ == "__main__":
    asyncio.run(main())