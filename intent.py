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
        'ai_response': ['what', 'how', 'why', 'tell me', 'explain', 'help'],
        'learn_preference': ['remember', 'my favorite', 'i like', 'my name is'],
        'get_preference': ['what is my', 'do you remember', 'what do you know about me'],
        'add_contact': ['add contact', 'new contact', 'save contact']
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
        """Use Gemini AI for more accurate intent detection with few-shot prompting."""
        
        # Define the list of possible intents
        possible_intents = [
            'greeting', 'time', 'joke', 'weather', 'open_app', 'volume', 
            'system_info', 'screenshot', 'shutdown', 'restart', 'exit', 'ai_response',
            'learn_preference', 'get_preference', 'add_contact'
        ]
        
        # Create a more detailed prompt with few-shot examples
        prompt = f"""As an advanced intent detector for a voice assistant, your task is to analyze the user's input and provide a precise JSON output.

## Instructions
1.  **Classify the Intent**: Determine the user's primary goal from the list of possible intents.
2.  **Extract Entities**: Identify key details (metadata) from the input.
3.  **JSON Output**: Respond ONLY with a valid JSON object containing the intent, confidence, and extracted parameters.

## Possible Intents
`{', '.join(possible_intents)}`

## Examples
User Input: "Hey Jarvis, what\'s the weather like in London?"
JSON Output:
{{
    "intent": "weather",
    "confidence": 0.95,
    "parameters": {{ "location": "London" }}
}}

User Input: "Can you open Google Chrome for me?"
JSON Output:
{{
    "intent": "open_app",
    "confidence": 0.98,
    "parameters": {{ "app_name": "chrome" }}
}}

User Input: "Remember my favorite color is blue"
JSON Output:
{{
    "intent": "learn_preference",
    "confidence": 0.97,
    "parameters": {{ "key": "favorite color", "value": "blue" }}
}}

User Input: "What is my favorite color?"
JSON Output:
{{
    "intent": "get_preference",
    "confidence": 0.96,
    "parameters": {{ "key": "favorite color" }}
}}

User Input: "Add a new contact named John Doe with phone 123-456-7890"
JSON Output:
{{
    "intent": "add_contact",
    "confidence": 0.98,
    "parameters": {{ "name": "John Doe", "phone": "123-456-7890" }}
}}

User Input: "What is the capital of France?"
JSON Output:
{{
    "intent": "ai_response",
    "confidence": 0.9,
    "parameters": {{}}
}}

## Current Task
User Input: "{user_input}"
Context: {context if context else "No previous context"}

Respond with the JSON output:
"""
        
        try:
            # Generate content using the Gemini model
            response = self.model.generate_content(prompt)
            
            # Clean up the response to ensure it's valid JSON
            cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
            
            # Parse the JSON response
            result = json.loads(cleaned_response)
            
            # Extract intent, confidence, and parameters
            intent = result.get('intent', 'ai_response')
            confidence = result.get('confidence', 0.75)
            parameters = result.get('parameters', {})
            
            # Ensure the detected intent is valid
            if intent not in possible_intents:
                intent = 'ai_response' # Default to AI response if intent is unknown
            
            return intent, confidence, parameters

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"⚠️  AI parsing failed: {e}. Falling back to keyword detection.")
            return self._keyword_based_detection(user_input)
        except Exception as e:
            print(f"⚠️  AI detection failed unexpectedly: {e}. Falling back to keyword detection.")
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
        words = user_input.split()
        
        if intent == 'open_app':
            apps = ['chrome', 'youtube', 'vscode', 'notepad', 'calculator', 'spotify']
            for app in apps:
                if app in user_input:
                    metadata['app_name'] = app
                    break
        
        elif intent == 'volume':
            import re
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                metadata['level'] = int(numbers[0])
            if 'mute' in user_input: metadata['action'] = 'mute'
            elif 'unmute' in user_input: metadata['action'] = 'unmute'
            elif 'increase' in user_input: metadata['action'] = 'increase'
            elif 'decrease' in user_input: metadata['action'] = 'decrease'
            elif 'set' in user_input: metadata['action'] = 'set'

        elif intent == 'weather':
            if 'in' in words:
                try:
                    idx = words.index('in')
                    metadata['location'] = ' '.join(words[idx+1:])
                except (ValueError, IndexError):
                    pass
        
        elif intent == 'learn_preference':
            # Example: "remember my name is John" -> key='name', value='John'
            try:
                if 'is' in words:
                    is_idx = words.index('is')
                    key_words = words[2:is_idx]
                    value_words = words[is_idx+1:]
                    metadata['key'] = ' '.join(key_words)
                    metadata['value'] = ' '.join(value_words)
            except (ValueError, IndexError):
                pass

        elif intent == 'get_preference':
            # Example: "what is my name" -> key='name'
            try:
                if 'my' in words:
                    my_idx = words.index('my')
                    metadata['key'] = ' '.join(words[my_idx+1:])
            except (ValueError, IndexError):
                pass
                
        elif intent == 'add_contact':
            # Example: "add contact John Doe phone 12345"
            try:
                name_idx = words.index('contact') + 1
                phone_idx = words.index('phone') + 1
                metadata['name'] = ' '.join(words[name_idx:phone_idx-1])
                metadata['phone'] = words[phone_idx]
            except (ValueError, IndexError):
                pass

        return metadata
    
    def get_ai_response(self, prompt: str, context: str = "") -> str:
        """Get a conversational response from Gemini."""
        if not self.use_ai:
            return "I\'m sorry, I need a valid API key to process that. Please configure your Gemini API key."
        
        try:
            # Add context to the prompt for better responses
            full_prompt = f"{context}\n\nUser query: {prompt}" if context else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"AI response error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"