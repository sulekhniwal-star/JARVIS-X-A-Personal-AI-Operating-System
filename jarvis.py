import asyncio
import datetime
import webbrowser
import os
import requests
import json
import re
import threading
import time
import logging
import platform
import subprocess
from collections import deque
import sqlite3
from datetime import datetime as dt
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JarvisSkillManager:
    def __init__(self):
        self.skills = {}
        self.load_default_skills()
    
    def register_skill(self, name, handler, keywords):
        self.skills[name] = {'handler': handler, 'keywords': keywords}
    
    def load_default_skills(self):
        self.register_skill('math', self.math_solver, ['calculate', 'math', 'solve'])
    
    def math_solver(self, query):
        try:
            math_expr = re.search(r'[0-9+\-*/().\s]+', query)
            if math_expr:
                result = eval(math_expr.group())
                return f"The answer is {result}"
        except:
            return "I couldn't solve that math problem"
        return "Please provide a valid math expression"
    
    def find_skill(self, command):
        for skill_name, skill_data in self.skills.items():
            for keyword in skill_data['keywords']:
                if keyword in command.lower():
                    return skill_data['handler']
        return None

class Jarvis:
    def __init__(self):
        self.listening = True
        self.conversation_memory = deque(maxlen=10)
        self.offline_mode = False
        
        # Initialize components
        self.skill_manager = JarvisSkillManager()
        
        # Initialize long-term memory database
        self.init_memory_db()
        
        # Custom commands storage
        self.custom_commands = self.load_custom_commands()
    
    def init_memory_db(self):
        try:
            self.conn = sqlite3.connect('jarvis_memory.db')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    category TEXT,
                    content TEXT,
                    importance INTEGER
                )
            ''')
            self.conn.commit()
        except Exception as e:
            logging.error(f"Memory DB init failed: {e}")
    
    def save_memory(self, category, content, importance=1):
        try:
            timestamp = dt.now().isoformat()
            self.conn.execute(
                "INSERT INTO memories (timestamp, category, content, importance) VALUES (?, ?, ?, ?)",
                (timestamp, category, content, importance)
            )
            self.conn.commit()
        except Exception as e:
            logging.error(f"Save memory failed: {e}")
    
    def recall_memory(self, query):
        try:
            cursor = self.conn.execute(
                "SELECT content FROM memories WHERE content LIKE ? ORDER BY importance DESC LIMIT 3",
                (f"%{query}%",)
            )
            memories = [row[0] for row in cursor.fetchall()]
            return memories
        except Exception as e:
            logging.error(f"Recall memory failed: {e}")
            return []
    
    def load_custom_commands(self):
        try:
            if os.path.exists('custom_commands.json'):
                with open('custom_commands.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load custom commands: {e}")
        return {}
    
    def save_custom_command(self, trigger, response):
        self.custom_commands[trigger] = response
        try:
            with open('custom_commands.json', 'w') as f:
                json.dump(self.custom_commands, f, indent=2)
            return f"Custom command '{trigger}' saved"
        except Exception as e:
            return f"Failed to save command: {e}"
    
    async def speak(self, text):
        print(f"🤖 Jarvis: {text}")
    
    def get_input(self):
        try:
            return input("👤 You: ").strip()
        except KeyboardInterrupt:
            return "exit"
        except Exception:
            return ""
    
    def get_time(self):
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}"
    
    def get_date(self):
        today = datetime.date.today()
        return f"Today is {today.strftime('%A, %B %d, %Y')}"
    
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
    
    async def process_command(self, command):
        if not command:
            return
        
        try:
            # Check custom commands first
            for trigger, response in self.custom_commands.items():
                if trigger.lower() in command.lower():
                    await self.speak(response)
                    return
            
            # Check skills
            skill_handler = self.skill_manager.find_skill(command)
            if skill_handler:
                result = skill_handler(command)
                await self.speak(result)
                return
            
            # Create custom command
            if "create command" in command:
                parts = command.split("create command", 1)[1].strip().split("response")
                if len(parts) == 2:
                    trigger = parts[0].strip()
                    response = parts[1].strip()
                    result = self.save_custom_command(trigger, response)
                    await self.speak(result)
                else:
                    await self.speak("Say: create command [trigger] response [response]")
                return
            
            # Basic commands
            if "time" in command:
                await self.speak(self.get_time())
            elif "date" in command:
                await self.speak(self.get_date())
            elif "weather" in command:
                result = self.get_weather(command)
                await self.speak(result)
            elif "search" in command:
                query = command.replace("search", "").strip()
                webbrowser.open(f"https://www.google.com/search?q={query}")
                await self.speak(f"Searching for {query}")
            elif "open" in command:
                if "notepad" in command:
                    if platform.system() == "Windows":
                        os.system("notepad")
                    await self.speak("Opening text editor")
                elif "calculator" in command:
                    if platform.system() == "Windows":
                        os.system("calc")
                    await self.speak("Opening calculator")
            elif "remember" in command:
                content = command.replace("remember", "").strip()
                self.save_memory('user_request', content, importance=2)
                await self.speak(f"I'll remember that: {content}")
            elif "what do you remember about" in command:
                query = command.replace("what do you remember about", "").strip()
                memories = self.recall_memory(query)
                if memories:
                    result = "I remember: " + ". ".join(memories[:2])
                else:
                    result = f"I don't have any memories about {query}"
                await self.speak(result)
            elif "help" in command:
                await self.speak("Available commands: time, date, weather in [city], search [query], open notepad/calculator, calculate [math], remember [fact], create command [trigger] response [response], help, exit")
            elif "shutdown" in command or "exit" in command or "quit" in command:
                await self.speak("Goodbye! Shutting down.")
                self.listening = False
            elif "hello" in command or "hi" in command:
                await self.speak("Hello! I'm Jarvis, your text-based AI assistant. Type 'help' for available commands.")
            else:
                await self.speak("I didn't understand that. Try: time, date, weather, search, calculate, or type 'help' for more commands.")
                    
        except Exception as e:
            logging.error(f"Command error: {e}")
            await self.speak("Sorry, I encountered an error.")
    
    async def run(self):
        await self.speak("🚀 Jarvis Text Assistant Online!")
        await self.speak("Type your commands below (no need to say 'Jarvis'). Type 'help' for available commands or 'exit' to quit.")
        print("-" * 50)
        
        while self.listening:
            try:
                command = self.get_input()
                if command:
                    await self.process_command(command)
                
            except KeyboardInterrupt:
                await self.speak("Goodbye!")
                if hasattr(self, 'conn'):
                    self.conn.close()
                break
            except Exception as e:
                logging.error(f"Main loop error: {e}")
                await asyncio.sleep(1)

async def main():
    jarvis = Jarvis()
    await jarvis.run()

if __name__ == "__main__":
    asyncio.run(main())