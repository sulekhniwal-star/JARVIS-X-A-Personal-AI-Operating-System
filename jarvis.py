import asyncio
import datetime
import logging
import os
import platform
import subprocess
import tempfile
from io import BytesIO
from typing import Optional, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    pass

try:
    import edge_tts  # type: ignore
except ImportError:
    edge_tts = None  # type: ignore

try:
    import google.generativeai as genai  # type: ignore
except ImportError:
    genai = None  # type: ignore

try:
    import pyautogui  # type: ignore
except ImportError:
    pyautogui = None  # type: ignore

try:
    import speech_recognition as sr  # type: ignore
except ImportError:
    sr = None  # type: ignore

try:
    from duckduckgo_search import DDGS  # type: ignore
except ImportError:
    DDGS = None  # type: ignore

try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    load_dotenv = None  # type: ignore

try:
    from PIL import Image  # type: ignore
except ImportError:
    Image = None  # type: ignore

try:
    import cv2  # type: ignore
except ImportError:
    cv2 = None  # type: ignore

try:
    import vosk  # type: ignore
except ImportError:
    vosk = None  # type: ignore

try:
    import psutil  # type: ignore
except ImportError:
    psutil = None  # type: ignore

try:
    import yfinance as yf  # type: ignore
except ImportError:
    yf = None  # type: ignore

try:
    import pywhatkit  # type: ignore
except ImportError:
    pywhatkit = None  # type: ignore

import json

# Load environment variables
if load_dotenv:
    load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JarvisAgent:
    """Modern Agentic AI Assistant using Gemini Function Calling"""

    def __init__(self):
        self.listening: bool = True
        self.memory: Dict[str, Any] = {}
        self.memory_file: str = "memory.json"

        # Check if speech recognition is available
        if not sr:
            print("Warning: speech_recognition package not installed. Speech recognition will not work. Run: pip install SpeechRecognition")

        self.recognizer = sr.Recognizer()  # type: ignore
        self.microphone = sr.Microphone()  # type: ignore

        # Initialize Vosk for offline wake word detection
        self.vosk_recognizer = None
        if vosk:
            try:
                # You may need to download a Vosk model (e.g., vosk-model-small-en-us-0.15)
                # For now, we'll assume it's in a 'model' directory
                model_path = "model"
                if os.path.exists(model_path):
                    self.vosk_recognizer = vosk.Model(model_path)  # type: ignore
                    logger.info("🤖 Vosk model loaded for offline wake word detection")
                else:
                    logger.warning("Vosk model not found. Wake word detection will use Google (online). Download a model from https://alphacephei.com/vosk/models")
            except Exception as e:
                logger.error(f"Failed to load Vosk model: {e}")
        else:
            logger.warning("Vosk not installed. Wake word detection will use Google (online).")

        # Initialize Gemini with function calling
        self._setup_gemini()

        logger.info("🤖 Jarvis Agent initialized with function calling capabilities")
    
    def _setup_gemini(self):
        """Configure Gemini with function calling tools"""
        if not genai:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
            
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)  # type: ignore
        
        # Define function schemas for Gemini
        self.tools: list[dict[str, Any]] = [  # type: ignore
            {
                "function_declarations": [
                    {
                        "name": "get_current_time",
                        "description": "Get the current date and time",
                        "parameters": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "get_weather",
                        "description": "Get weather information for a location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {"type": "string", "description": "City or location name"}
                            },
                            "required": ["location"]
                        }
                    },
                    {
                        "name": "web_search",
                        "description": "Search the internet for information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query"}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "open_application",
                        "description": "Open an application or program",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "app_name": {"type": "string", "description": "Name of the application to open"}
                            },
                            "required": ["app_name"]
                        }
                    },
                    {
                        "name": "analyze_screen",
                        "description": "Take a screenshot and analyze what's on the screen",
                        "parameters": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "analyze_webcam",
                        "description": "Capture a frame from the webcam and analyze it",
                        "parameters": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "remember_fact",
                        "description": "Remember a fact or information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string", "description": "Key for the memory"},
                                "value": {"type": "string", "description": "Value to remember"}
                            },
                            "required": ["key", "value"]
                        }
                    },
                    {
                        "name": "recall_memory",
                        "description": "Recall a remembered fact",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string", "description": "Key to recall"}
                            },
                            "required": ["key"]
                        }
                    },
                    {
                        "name": "get_battery_status",
                        "description": "Get the current battery status",
                        "parameters": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "shutdown_system",
                        "description": "Shutdown the system",
                        "parameters": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "restart_system",
                        "description": "Restart the system",
                        "parameters": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "sleep_system",
                        "description": "Put the system to sleep",
                        "parameters": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "system_control",
                        "description": "Control system functions like volume, screenshot, etc.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "description": "System action to perform"}
                            },
                            "required": ["action"]
                        }
                    },
                    {
                        "name": "play_youtube",
                        "description": "Play a video or song on YouTube",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "topic": {"type": "string", "description": "The name of the video or song to play"}
                            },
                            "required": ["topic"]
                        }
                    },
                    {
                        "name": "get_stock_price",
                        "description": "Get the current stock price of a company",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "ticker": {"type": "string", "description": "The stock ticker symbol (e.g., AAPL, GOOGL)"}
                            },
                            "required": ["ticker"]
                        }
                    },
                    {
                        "name": "check_system_health",
                        "description": "Check CPU and RAM usage",
                        "parameters": {"type": "object", "properties": {}}
                    }
                ]
            }
        ]
        
        # Initialize Gemini models
        self.chat_model = genai.GenerativeModel(  # type: ignore
            'gemini-1.5-flash',
            tools=self.tools,
            system_instruction="You are Jarvis, an intelligent AI assistant. Use the available functions when appropriate to help the user. Be concise and helpful."
        )
        
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')  # type: ignore
        
        # Start chat session
        self.chat = self.chat_model.start_chat()  # type: ignore
    
    async def listen_for_speech(self) -> Optional[str]:
        """Listen for speech input asynchronously"""
        try:
            with self.microphone as source:  # type: ignore
                self.recognizer.adjust_for_ambient_noise(source, duration=1)  # type: ignore

            # Run speech recognition in thread pool to avoid blocking
            loop = asyncio.get_event_loop()

            def listen():  # type: ignore
                with self.microphone as source:  # type: ignore
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)  # type: ignore
                return self.recognizer.recognize_google(audio)  # type: ignore

            text = await loop.run_in_executor(None, listen)  # type: ignore
            logger.info(f"👤 User said: {text}")
            return text.lower()  # type: ignore

        except sr.WaitTimeoutError:  # type: ignore
            return None
        except sr.UnknownValueError:  # type: ignore
            return None
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return None
    
    async def speak(self, text: str, voice: str = "en-US-AriaNeural") -> None:
        """Convert text to speech and play using system audio"""
        try:
            logger.info(f"🤖 Jarvis: {text}")
            
            if edge_tts is None:
                print(f"🤖 Jarvis: {text}")
                return
            
            # Generate speech
            communicate = edge_tts.Communicate(text, voice)  # type: ignore
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                async for chunk in communicate.stream():  # type: ignore
                    if chunk["type"] == "audio":  # type: ignore
                        temp_file.write(chunk["data"])  # type: ignore
                temp_path = temp_file.name
            
            # Play using system audio player
            system = platform.system().lower()
            if system == "windows":
                subprocess.run(["powershell", "-c", f"(New-Object Media.SoundPlayer '{temp_path}').PlaySync()"], 
                             check=False, capture_output=True)
            elif system == "darwin":
                subprocess.run(["afplay", temp_path], check=False)
            elif system == "linux":
                subprocess.run(["aplay", temp_path], check=False)
            
            # Cleanup
            await asyncio.sleep(0.5)  # Brief delay before cleanup
            try:
                os.unlink(temp_path)
            except:
                pass
            
        except Exception as e:
            logger.error(f"Speech synthesis error: {e}")
            print(f"🤖 Jarvis: {text}")  # Fallback to text
    
    # Tool Functions
    async def get_current_time(self) -> str:
        """Get current date and time"""
        now = datetime.datetime.now()
        return f"Current time: {now.strftime('%I:%M %p on %A, %B %d, %Y')}"
    
    async def get_weather(self, location: str) -> str:
        """Get weather information using free service"""
        try:
            import requests  # type: ignore
            url = f"http://wttr.in/{location}?format=%C+%t+%h+%w+in+%l"
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: requests.get(url, timeout=5)
            )
            
            if response.status_code == 200:
                return f"Weather in {location}: {response.text.strip()}"
            else:
                return f"Could not get weather for {location}"
                
        except Exception as e:
            logger.error(f"Weather error: {e}")
            return f"Weather service unavailable for {location}"
    
    async def web_search(self, query: str) -> str:
        """Search the web using DuckDuckGo"""
        try:
            loop = asyncio.get_event_loop()
            
            def search():  # type: ignore
                with DDGS() as ddgs:  # type: ignore
                    results = list(ddgs.text(query, max_results=3))  # type: ignore
                    return results  # type: ignore
            
            results = await loop.run_in_executor(None, search)  # type: ignore
            
            if results:  # type: ignore
                formatted_results = []  # type: ignore
                for i, result in enumerate(results[:3], 1):  # type: ignore
                    formatted_results.append(f"{i}. {result['title']}: {result['body'][:100]}...")  # type: ignore
                
                return f"Search results for '{query}':\n" + "\n".join(formatted_results)  # type: ignore
            else:
                return f"No search results found for '{query}'"
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Search service unavailable for '{query}'"
    
    async def open_application(self, app_name: str) -> str:
        """Open an application"""
        try:
            system = platform.system().lower()
            
            # Common application mappings
            app_mappings = {
                "notepad": {"windows": "notepad", "darwin": "TextEdit", "linux": "gedit"},
                "calculator": {"windows": "calc", "darwin": "Calculator", "linux": "gnome-calculator"},
                "browser": {"windows": "start chrome", "darwin": "open -a 'Google Chrome'", "linux": "google-chrome"},
                "code": {"windows": "code", "darwin": "code", "linux": "code"},
                "spotify": {"windows": "spotify", "darwin": "open -a Spotify", "linux": "spotify"}
            }
            
            app_lower = app_name.lower()
            if app_lower in app_mappings and system in app_mappings[app_lower]:
                command = app_mappings[app_lower][system]
            else:
                command = app_name
            
            # Run command asynchronously
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return f"Opened {app_name}"
            
        except Exception as e:
            logger.error(f"App opening error: {e}")
            return f"Could not open {app_name}"
    
    async def analyze_screen(self) -> str:
        """Take screenshot and analyze with Gemini Vision"""
        try:
            if Image is None:
                return "PIL not available for image processing"

            # Take screenshot
            screenshot = pyautogui.screenshot()  # type: ignore

            # Convert to bytes
            img_buffer = BytesIO()
            screenshot.save(img_buffer, format='PNG')  # type: ignore
            img_buffer.seek(0)

            # Analyze with Gemini Vision
            image = Image.open(img_buffer)  # type: ignore
            
            response = await asyncio.get_event_loop().run_in_executor(  # type: ignore[misc]
                None,
                lambda: self.vision_model.generate_content([  # type: ignore
                    "Analyze this screenshot and describe what you see. Be concise and focus on the main elements.",
                    image
                ])  # type: ignore
            )  # type: ignore

            return f"Screen analysis: {response.text}"  # type: ignore
            
        except Exception as e:
            logger.error(f"Screen analysis error: {e}")
            return "Could not analyze screen"
    
    async def system_control(self, action: str) -> str:
        """Control system functions"""
        try:
            action_lower = action.lower()

            if "volume up" in action_lower:
                if platform.system() == "Windows":
                    pyautogui.press('volumeup')  # type: ignore
                return "Volume increased"

            elif "volume down" in action_lower:
                if platform.system() == "Windows":
                    pyautogui.press('volumedown')  # type: ignore
                return "Volume decreased"

            elif "screenshot" in action_lower:
                screenshot = pyautogui.screenshot()  # type: ignore
                filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                screenshot.save(filename)  # type: ignore
                return f"Screenshot saved as {filename}"

            else:
                return f"Unknown system action: {action}"

        except Exception as e:
            logger.error(f"System control error: {e}")
            return f"System control failed: {action}"

    def load_memory(self) -> Dict[str, Any]:
        """Load memory from JSON file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
            return {}

    def save_memory(self):
        """Save memory to JSON file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")

    async def analyze_webcam(self) -> str:
        """Capture a frame from the webcam and analyze with Gemini Vision"""
        try:
            if cv2 is None:
                return "OpenCV not available for webcam analysis"

            if Image is None:
                return "PIL not available for image processing"

            # Capture frame from webcam
            cap = cv2.VideoCapture(0)  # type: ignore
            if not cap.isOpened():  # type: ignore
                return "Could not access webcam"

            ret, frame = cap.read()  # type: ignore
            cap.release()  # type: ignore

            if not ret:
                return "Failed to capture frame from webcam"

            # Convert to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # type: ignore
            pil_image = Image.fromarray(frame_rgb)  # type: ignore

            # Analyze with Gemini Vision
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.vision_model.generate_content([  # type: ignore
                    "Analyze this webcam image and describe what you see. Be concise and focus on the main elements.",
                    pil_image
                ])
            )

            return f"Webcam analysis: {response.text}"

        except Exception as e:
            logger.error(f"Webcam analysis error: {e}")
            return "Could not analyze webcam"

    async def remember_fact(self, key: str, value: str) -> str:
        """Remember a fact"""
        self.memory[key] = value
        self.save_memory()
        return f"Remembered: {key} = {value}"

    async def recall_memory(self, key: str) -> str:
        """Recall a remembered fact"""
        if key in self.memory:
            return f"{key}: {self.memory[key]}"
        else:
            return f"No memory found for {key}"

    async def get_battery_status(self) -> str:
        """Get battery status"""
        try:
            if psutil is None:
                return "psutil not available for battery status"

            battery = psutil.sensors_battery()  # type: ignore
            if battery is None:
                return "Battery information not available"

            percent = battery.percent  # type: ignore
            plugged = battery.power_plugged  # type: ignore
            status = "Plugged in" if plugged else "On battery"
            return f"Battery: {percent}% - {status}"

        except Exception as e:
            logger.error(f"Battery status error: {e}")
            return "Could not get battery status"

    async def shutdown_system(self) -> str:
        """Shutdown the system"""
        try:
            system = platform.system().lower()
            if system == "windows":
                subprocess.run(["shutdown", "/s", "/t", "0"], check=False)
            elif system == "darwin":
                subprocess.run(["sudo", "shutdown", "-h", "now"], check=False)
            elif system == "linux":
                subprocess.run(["sudo", "shutdown", "-h", "now"], check=False)
            return "System shutting down"
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
            return "Could not shutdown system"

    async def restart_system(self) -> str:
        """Restart the system"""
        try:
            system = platform.system().lower()
            if system == "windows":
                subprocess.run(["shutdown", "/r", "/t", "0"], check=False)
            elif system == "darwin":
                subprocess.run(["sudo", "shutdown", "-r", "now"], check=False)
            elif system == "linux":
                subprocess.run(["sudo", "shutdown", "-r", "now"], check=False)
            return "System restarting"
        except Exception as e:
            logger.error(f"Restart error: {e}")
            return "Could not restart system"

    async def sleep_system(self) -> str:
        """Put the system to sleep"""
        try:
            system = platform.system().lower()
            if system == "windows":
                subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=False)
            elif system == "darwin":
                subprocess.run(["pmset", "sleepnow"], check=False)
            elif system == "linux":
                subprocess.run(["systemctl", "suspend"], check=False)
            return "System going to sleep"
        except Exception as e:
            logger.error(f"Sleep error: {e}")
            return "Could not put system to sleep"

    async def play_youtube(self, topic: str) -> str:
        """Play a video on YouTube"""
        if pywhatkit is None:
            return "pywhatkit not available for YouTube playback"
        try:
            # pywhatkit runs synchronously, so we run it in an executor
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: pywhatkit.playonyt(topic)  # type: ignore
            )
            return f"Playing {topic} on YouTube."
        except Exception as e:
            logger.error(f"YouTube error: {e}")
            return "Failed to play video."

    async def get_stock_price(self, ticker: str) -> str:
        """Get stock price using yfinance"""
        if yf is None:
            return "yfinance not available for stock prices"
        try:
            stock = yf.Ticker(ticker)  # type: ignore
            info = stock.info  # type: ignore
            price = info.get('currentPrice') or info.get('regularMarketPrice')  # type: ignore
            return f"The current price of {ticker.upper()} is ${price}."
        except Exception as _:
            return f"Could not find stock data for {ticker}."

    async def check_system_health(self) -> str:
        """Check CPU and RAM"""
        if psutil is None:
            return "psutil not available for system health check"
        cpu_usage = psutil.cpu_percent(interval=1)  # type: ignore
        ram_usage = psutil.virtual_memory().percent  # type: ignore
        return f"System Health: CPU is at {cpu_usage}%, and RAM is at {ram_usage}%."
    
    async def execute_function_call(self, function_call) -> str:  # type: ignore
        """Execute a function call from Gemini"""
        function_name = function_call.name  # type: ignore
        args = dict(function_call.args) if function_call.args else {}  # type: ignore
        
        logger.info(f"🔧 Executing function: {function_name} with args: {args}")
        
        # Map function names to methods
        function_map = {  # type: ignore
            "get_current_time": self.get_current_time,
            "get_weather": self.get_weather,
            "web_search": self.web_search,
            "open_application": self.open_application,
            "analyze_screen": self.analyze_screen,
            "analyze_webcam": self.analyze_webcam,
            "remember_fact": self.remember_fact,
            "recall_memory": self.recall_memory,
            "get_battery_status": self.get_battery_status,
            "shutdown_system": self.shutdown_system,
            "restart_system": self.restart_system,
            "sleep_system": self.sleep_system,
            "system_control": self.system_control,
            "play_youtube": self.play_youtube,
            "get_stock_price": self.get_stock_price,
            "check_system_health": self.check_system_health
        }
        
        if function_name in function_map:
            try:
                if args:
                    result = await function_map[function_name](**args)  # type: ignore
                else:
                    result = await function_map[function_name]()  # type: ignore
                return result  # type: ignore
            except Exception as e:
                logger.error(f"Function execution error: {e}")
                return f"Error executing {function_name}: {str(e)}"
        else:
            return f"Unknown function: {function_name}"
    
    async def process_with_gemini(self, user_input: str) -> str:
        """Process user input with Gemini and handle function calls"""
        try:
            # Send message to Gemini
            response: "GenerateContentResponse" = await asyncio.get_event_loop().run_in_executor(  # type: ignore
                None,
                lambda: self.chat.send_message(user_input)  # type: ignore
            )  # type: ignore
            
            # Check if Gemini wants to call functions
            if response.candidates[0].content.parts:  # type: ignore
                for part in response.candidates[0].content.parts:  # type: ignore
                    if hasattr(part, 'function_call'):  # type: ignore
                        # Execute the function call
                        function_result = await self.execute_function_call(part.function_call)  # type: ignore
                        
                        # Send function result back to Gemini
                        function_response = await asyncio.get_event_loop().run_in_executor(  # type: ignore
                            None,
                            lambda: self.chat.send_message([  # type: ignore
                                genai.protos.Part(  # type: ignore
                                    function_response=genai.protos.FunctionResponse(  # type: ignore
                                        name=part.function_call.name,  # type: ignore
                                        response={"result": function_result}
                                    )
                                )
                            ])
                        )  # type: ignore
                        
                        return function_response.text  # type: ignore
                    
                    elif hasattr(part, 'text'):  # type: ignore
                        return part.text  # type: ignore
            
            return response.text  # type: ignore
            
        except Exception as e:
            logger.error(f"Gemini processing error: {e}")
            return "I'm having trouble processing that request right now."
    
    async def wait_for_wake_word(self) -> bool:
        """Wait for wake word 'jarvis' or 'hey jarvis' using Vosk (offline)"""
        if self.vosk_recognizer:  # type: ignore
            # Use Vosk for offline wake word detection
            try:
                with self.microphone as source:  # type: ignore
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)  # type: ignore
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)  # type: ignore

                    # Convert audio to raw data for Vosk
                    audio_data = audio.get_raw_data()  # type: ignore
                    if self.vosk_recognizer.AcceptWaveform(audio_data):  # type: ignore
                        result = json.loads(self.vosk_recognizer.Result())  # type: ignore
                        text = result.get("text", "").lower()
                        if "jarvis" in text or "hey jarvis" in text:
                            logger.info(f"🤖 Wake word detected (Vosk): {text}")
                            return True
            except Exception as e:
                logger.error(f"Vosk wake word detection error: {e}")
                # Fallback to Google
                speech = await self.listen_for_speech()
                if speech and ("jarvis" in speech or "hey jarvis" in speech):
                    return True
        else:
            # Fallback to Google speech recognition
            speech = await self.listen_for_speech()
            if speech and ("jarvis" in speech or "hey jarvis" in speech):
                return True
        return False
    
    async def run(self):
        """Main agent loop"""
        await self.speak("Jarvis Agent online. I'm ready to assist you with intelligent function calling.")
        
        while self.listening:
            try:
                # Wait for wake word
                if await self.wait_for_wake_word():
                    await self.speak("Yes, how can I help?")
                    
                    # Listen for command
                    command = await self.listen_for_speech()
                    
                    if command:
                        # Remove wake words
                        command = command.replace("jarvis", "").replace("hey", "").strip()
                        
                        if "shutdown" in command or "exit" in command:
                            await self.speak("Goodbye!")
                            self.listening = False
                            break
                        
                        # Process with Gemini
                        response = await self.process_with_gemini(command)
                        await self.speak(response)
                
                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                await self.speak("Shutting down Jarvis Agent.")
                self.listening = False
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(1)

async def main():
    """Entry point"""
    try:
        agent = JarvisAgent()
        await agent.run()
    except Exception as e:
        logger.error(f"Failed to start Jarvis Agent: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())