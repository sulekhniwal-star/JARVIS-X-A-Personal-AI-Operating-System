"""
Advanced NLP Intent Detection
============================
Upgrade 2: AI Intent Understanding
- Better phrase mapping to intents
- Context-aware detection
- Learning from user patterns
"""

import google.generativeai as genai
import json
import re
from typing import Tuple, Dict, Any, List
from datetime import datetime

class AdvancedIntentDetector:
    """Enhanced intent detection with learning capabilities."""
    
    # Expanded intent patterns
    INTENT_PATTERNS = {
        'greeting': {
            'patterns': ['hello', 'hi', 'hey', 'good morning', 'good evening', 'namaste', 'what\s up', 'how are you'],
            'responses': ['Hello! How can I help?', 'Hi there!', 'Good to see you!']
        },
        'time': {
            'patterns': ['time', 'what time', 'current time', 'clock', 'what\s the time'],
            'responses': ['The current time is {}']
        },
        'date': {
            'patterns': ['date', 'what date', 'today', 'what day'],
            'responses': ['Today is {}']
        },
        'weather': {
            'patterns': ['weather', 'temperature', 'rain', 'forecast', 'climate', 'hot', 'cold'],
            'responses': ['Let me check the weather for you']
        },
        'open_browser': {
            'patterns': ['open chrome', 'launch browser', 'start chrome', 'open google', 'browse internet'],
            'app': 'chrome'
        },
        'open_youtube': {
            'patterns': ['open youtube', 'launch youtube', 'youtube', 'watch videos'],
            'app': 'youtube'
        },
        'open_music': {
            'patterns': ['play music', 'open spotify', 'music', 'songs', 'tune'],
            'app': 'spotify'
        },
        'open_code': {
            'patterns': ['open vscode', 'code editor', 'programming', 'vs code', 'coding'],
            'app': 'vscode'
        },
        'volume_up': {
            'patterns': ['volume up', 'increase volume', 'louder', 'turn up', 'raise volume'],
            'action': 'increase'
        },
        'volume_down': {
            'patterns': ['volume down', 'decrease volume', 'quieter', 'turn down', 'lower volume'],
            'action': 'decrease'
        },
        'mute': {
            'patterns': ['mute', 'silence', 'turn off sound', 'no sound'],
            'action': 'mute'
        },
        'system_info': {
            'patterns': ['system info', 'computer specs', 'hardware', 'memory usage', 'cpu'],
            'responses': ['Let me check your system information']
        },
        'screenshot': {
            'patterns': ['screenshot', 'capture screen', 'take picture', 'screen capture'],
            'responses': ['Taking a screenshot']
        },
        'joke': {
            'patterns': ['joke', 'funny', 'make me laugh', 'tell joke', 'humor'],
            'responses': ['Here\s a joke for you']
        },
        'news': {
            'patterns': ['news', 'headlines', 'current events', 'what\s happening'],
            'responses': ['Let me get the latest news']
        },
        'reminder': {
            'patterns': ['remind me', 'set reminder', 'don\t forget', 'remember'],
            'responses': ['I\ll remind you about that']
        },
        'search': {
            'patterns': ['search for', 'look up', 'find', 'google', 'what is'],
            'responses': ['Searching for that information']
        },
        'shutdown': {
            'patterns': ['shutdown', 'turn off computer', 'power off', 'shut down'],
            'responses': ['Shutting down the system']
        },
        'restart': {
            'patterns': ['restart', 'reboot', 'restart computer'],
            'responses': ['Restarting the system']
        },
        'exit': {
            'patterns': ['exit', 'quit', 'goodbye', 'bye', 'close jarvis', 'stop'],
            'responses': ['Goodbye! Have a great day!']
        }
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.use_ai = api_key != "YOUR_GEMINI_API_KEY"
        self.learned_patterns = {}
        self.context_history = []
    
    def detect_intent(self, user_input: str, context: str = "") -> Tuple[str, float, Dict[str, Any]]:
        """Enhanced intent detection with context."""
        user_input = user_input.lower().strip()
        
        # Add to context history
        self.context_history.append(user_input)
        if len(self.context_history) > 5:
            self.context_history.pop(0)
        
        # Try AI detection first
        if self.use_ai:
            try:
                return self._ai_enhanced_detection(user_input, context)
            except Exception as e:
                print(f"AI detection failed: {e}")
        
        # Fallback to pattern matching
        return self._pattern_based_detection(user_input)
    
    def _ai_enhanced_detection(self, user_input: str, context: str) -> Tuple[str, float, Dict[str, Any]]:
        """AI-powered intent detection with context."""
        
        # Build context from history
        recent_context = " ".join(self.context_history[-3:])
        
        prompt = f"""
You are an advanced intent classifier for a voice assistant named JARVIS.

Available intents: {list(self.INTENT_PATTERNS.keys())}

User input: "{user_input}"
Recent context: "{recent_context}"
Additional context: "{context}"

Analyze the input and classify the intent. Consider:
1. Direct commands vs conversational requests
2. Context from previous interactions
3. Implied actions (e.g., "I'm cold" might mean adjust temperature)

Respond with valid JSON only:
{{
    "intent": "detected_intent",
    "confidence": 0.0-1.0,
    "entities": {{"entity_type": "value"}},
    "reasoning": "brief explanation"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            
            intent = result.get('intent', 'ai_response')
            confidence = result.get('confidence', 0.7)
            entities = result.get('entities', {})
            
            # Learn from high-confidence detections
            if confidence > 0.8:
                self._learn_pattern(user_input, intent)
            
            return intent, confidence, entities
            
        except Exception as e:
            print(f"AI detection error: {e}")
            return self._pattern_based_detection(user_input)
    
    def _pattern_based_detection(self, user_input: str) -> Tuple[str, float, Dict[str, Any]]:
        """Enhanced pattern-based detection."""
        
        # Check learned patterns first
        for pattern, intent in self.learned_patterns.items():
            if pattern in user_input:
                return intent, 0.9, self._extract_entities(intent, user_input)
        
        # Check built-in patterns
        best_match = None
        best_score = 0
        
        for intent, data in self.INTENT_PATTERNS.items():
            patterns = data.get('patterns', [])
            for pattern in patterns:
                # Use regex for better matching
                if re.search(r'\b' + pattern.replace('\\s', r'\s+') + r'\b', user_input):
                    score = len(pattern) / len(user_input)  # Longer matches get higher scores
                    if score > best_score:
                        best_score = score
                        best_match = intent
        
        if best_match:
            entities = self._extract_entities(best_match, user_input)
            return best_match, min(best_score * 2, 0.95), entities
        
        # Default to AI response
        return 'ai_response', 0.5, {}
    
    def _extract_entities(self, intent: str, user_input: str) -> Dict[str, Any]:
        """Extract entities based on intent."""
        entities = {}
        
        # Extract numbers
        numbers = re.findall(r'\d+', user_input)
        if numbers:
            entities['number'] = int(numbers[0])
        
        # Extract locations for weather
        if intent == 'weather':
            location_match = re.search(r'\bin\s+(\w+)', user_input)
            if location_match:
                entities['location'] = location_match.group(1)
        
        # Extract app names
        if 'open_' in intent:
            app_data = self.INTENT_PATTERNS.get(intent, {})
            entities['app'] = app_data.get('app', '')
        
        # Extract volume actions
        if 'volume' in intent or intent == 'mute':
            action_data = self.INTENT_PATTERNS.get(intent, {})
            entities['action'] = action_data.get('action', '')
            if numbers:
                entities['level'] = int(numbers[0])
        
        # Extract search queries
        if intent == 'search':
            search_patterns = [r'search for (.+)', r'look up (.+)', r'what is (.+)', r'find (.+)']
            for pattern in search_patterns:
                match = re.search(pattern, user_input)
                if match:
                    entities['query'] = match.group(1).strip()
                    break
        
        # Extract reminder content
        if intent == 'reminder':
            reminder_patterns = [r'remind me to (.+)', r'remind me about (.+)', r'don\'t forget (.+)']
            for pattern in reminder_patterns:
                match = re.search(pattern, user_input)
                if match:
                    entities['reminder_text'] = match.group(1).strip()
                    break
        
        return entities
    
    def _learn_pattern(self, user_input: str, intent: str):
        """Learn new patterns from successful detections."""
        # Extract key phrases (3+ words)
        words = user_input.split()
        if len(words) >= 3:
            key_phrase = ' '.join(words[:3])
            self.learned_patterns[key_phrase] = intent
    
    def get_contextual_response(self, intent: str, entities: Dict[str, Any], user_input: str) -> str:
        """Generate contextual responses."""
        
        if not self.use_ai:
            # Use predefined responses
            intent_data = self.INTENT_PATTERNS.get(intent, {})
            responses = intent_data.get('responses', ['I understand.'])
            return responses[0] if responses else 'I understand.'
        
        try:
            prompt = f"""
Generate a natural, helpful response for JARVIS voice assistant.

Intent: {intent}
User said: "{user_input}"
Extracted entities: {entities}
Context: {' '.join(self.context_history[-2:])}

Respond as JARVIS would - helpful, intelligent, and concise (max 2 sentences).
"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"Response generation error: {e}")
            return "I understand your request."
    
    def add_custom_intent(self, intent_name: str, patterns: List[str], response: str = None):
        """Add custom intent patterns."""
        self.INTENT_PATTERNS[intent_name] = {
            'patterns': patterns,
            'responses': [response] if response else ['Custom action executed']
        }
        print(f"✅ Added custom intent: {intent_name}")