import google.generativeai as genai
import json
from typing import Tuple, Dict, Any


class IntentDetector:
    """AI-powered intent detection using Gemini API."""
    
    # Enhanced intent patterns
    INTENT_KEYWORDS = {
        'greeting': ['hello', 'hi', 'hey', 'good morning', 'good evening', 'namaste'],
        'time': ['time', 'what time', 'current time', 'what\'s the time'],
        'joke': ['joke', 'make me laugh', 'funny', 'tell a joke'],
        'weather': ['weather', 'temperature', 'rain', 'forecast', 'how\'s the weather'],
        'open_app': ['open', 'launch', 'start'],
        'volume': ['volume', 'mute', 'unmute', 'sound'],
        'system_info': ['system info', 'system status', 'cpu', 'memory', 'performance'],
        'screenshot': ['screenshot', 'capture screen', 'take picture'],
        'shutdown': ['shutdown', 'turn off', 'power off', 'sleep'],
        'restart': ['restart', 'reboot'],
        'exit': ['exit', 'quit', 'goodbye', 'bye'],
        'ai_response': ['what', 'how', 'why', 'tell me', 'explain', 'help']
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)  # type: ignore
        # Use gemini-1.5-flash (compatible with free tier)
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # type: ignore
        self.use_ai = True if api_key != "YOUR_GEMINI_API_KEY" else False
    
    def detect_intent(self, user_input: str, context: str = "") -> Tuple[str, float, Dict[str, Any]]:
        """
        Detect intent using AI with fallback to keyword matching.
        Returns: (intent, confidence, metadata)
        """
        if not self.use_ai:
            # Use keyword-based detection
            return self._keyword_based_detection(user_input)
        
        try:
            # Use AI for more accurate detection
            return self._ai_based_detection(user_input, context)
        except Exception as e:
            print(f"AI detection failed: {e}, falling back to keyword detection")
            return self._keyword_based_detection(user_input)
    
    def _ai_based_detection(self, user_input: str, context: str) -> Tuple[str, float, Dict[str, Any]]:
        """Use Gemini AI for intent detection."""
        prompt = f"""You are a smart assistant intent detector. Analyze the user's input and classify it.

User input: "{user_input}"
Context: {context if context else "No previous context"}

Respond ONLY with valid JSON (no markdown, no extra text):
{{
    "intent": "one_of_these: greeting, time, joke, weather, open_app, volume, system_info, screenshot, shutdown, restart, exit, ai_response",
    "confidence": 0.0-1.0,
    "app_name": "if open_app intent, specify app name, else null",
    "action": "specific action if applicable, else null",
    "parameters": {{"key": "value"}} or {{}}
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            
            return (
                result.get('intent', 'ai_response'),
                result.get('confidence', 0.7),
                result.get('parameters', {})
            )
        except (json.JSONDecodeError, ValueError, KeyError):
            # Fallback if AI response is malformed
            return self._keyword_based_detection(user_input)
    
    def _keyword_based_detection(self, user_input: str) -> Tuple[str, float, Dict[str, Any]]:
        """Fallback keyword-based intent detection."""
        user_input = user_input.lower()
        
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in user_input:
                    # Extract metadata based on intent
                    metadata = self._extract_metadata(intent, user_input)
                    return intent, 0.6, metadata
        
        # Default to AI response if no keywords match
        return 'ai_response', 0.5, {}
    
    def _extract_metadata(self, intent: str, user_input: str) -> Dict[str, Any]:
        """Extract relevant metadata from user input."""
        metadata = {}
        
        if intent == 'open_app':
            # Extract app name
            apps = ['chrome', 'youtube', 'vscode', 'notepad', 'calculator', 'spotify']
            for app in apps:
                if app in user_input:
                    metadata['app_name'] = app
                    break
        
        elif intent == 'volume':
            # Extract volume level
            import re
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                metadata['level'] = int(numbers[0])
            
            if 'mute' in user_input:
                metadata['action'] = 'mute'
            elif 'unmute' in user_input:
                metadata['action'] = 'unmute'
            elif ('set' in user_input or 'change' in user_input) and numbers:
                # "set to X" or "change to X"
                metadata['action'] = 'set'
            elif 'increase' in user_input or 'louder' in user_input or 'turn up' in user_input:
                # "increase by X" or just "increase"
                if numbers and ('by' in user_input or 'to' not in user_input):
                    # "increase by 10" - use level as increment
                    metadata['increment'] = int(numbers[0])
                    metadata['action'] = 'increase_by'
                else:
                    # "increase to X" or just "increase"
                    metadata['action'] = 'increase'
            elif 'decrease' in user_input or 'lower' in user_input or 'turn down' in user_input or 'quiet' in user_input:
                # "decrease by X" or just "decrease"
                if numbers and ('by' in user_input or 'to' not in user_input):
                    # "decrease by 10" - use level as decrement
                    metadata['increment'] = int(numbers[0])
                    metadata['action'] = 'decrease_by'
                else:
                    # "decrease to X" or just "decrease"
                    metadata['action'] = 'decrease'
        
        elif intent == 'weather':
            # Try to extract location
            words = user_input.split()
            for i, word in enumerate(words):
                if word == 'in' and i + 1 < len(words):
                    metadata['location'] = ' '.join(words[i+1:])
                    break
        
        return metadata
    
    def get_ai_response(self, prompt: str, context: str = "") -> str:
        """Get a conversational response from Gemini."""
        if not self.use_ai:
            return "I'm sorry, I need a valid API key to process that. Please configure your Gemini API key."
        
        try:
            # Add context to the prompt for better responses
            full_prompt = f"{context}\n\nUser query: {prompt}" if context else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"AI response error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
