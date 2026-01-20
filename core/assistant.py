"""Main Jarvis assistant."""

import os
from core.speech_to_text import SpeechToText
from core.text_to_speech import TextToSpeech
from core.gemini_llm import GeminiLLM
from core.wake_word_detector import WakeWordDetector
from core.intent_classifier import IntentClassifier
from core.personality import PersonalityManager
from core.self_coder import SelfCoder
from core.agent_mode import AgentMode
from utils.memory import Memory
from utils.persistent_memory import PersistentMemory
from utils.file_indexer import FileIndexer
from utils.goals import GoalsManager
from skills.web_search import search_web
from skills.time_date import get_time_date
from skills.system_control import open_app
from skills import pc_control

class JarvisAssistant:
    def __init__(self):
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.llm = GeminiLLM()
        self.wake_detector = WakeWordDetector()
        self.intent_classifier = IntentClassifier()
        self.personality = PersonalityManager()
        self.self_coder = SelfCoder()
        self.memory = Memory()
        self.persistent_memory = PersistentMemory()
        self.file_indexer = FileIndexer("C:\\")
        self.goals_manager = GoalsManager()
        self.sleeping = False
        self.last_command = None
    
    def _get_combined_context(self) -> str:
        """Get combined context from persistent and short-term memory."""
        # Get persistent memory
        persistent = self.persistent_memory.fetch_last(5)
        persistent_context = "\n".join([f"User: {user}\nJarvis: {jarvis}" for user, jarvis in persistent])
        
        # Get short-term memory
        short_term_context = self.memory.get_context()
        
        # Combine contexts
        combined = f"{persistent_context}\n{short_term_context}" if persistent_context else short_term_context
        
        # Trim to 2000 characters from oldest side
        if len(combined) > 2000:
            combined = combined[-2000:]
        
        return combined
    
    def _run_diagnostics(self):
        """Run system diagnostics and report status."""
        failed_systems = []
        
        # Test TTS
        try:
            self.tts.speak("Testing voice system.")
        except Exception:
            failed_systems.append("voice system")
        
        # Test Gemini API
        try:
            response = self.llm.generate_reply("Reply with: Gemini OK", "")
            if "OK" not in response:
                failed_systems.append("Gemini API")
        except Exception:
            failed_systems.append("Gemini API")
        
        # Test SQLite memory
        try:
            self.persistent_memory.save("test_user", "test_jarvis")
            last_interactions = self.persistent_memory.fetch_last(1)
            if not last_interactions or last_interactions[0][0] != "test_user":
                failed_systems.append("SQLite memory")
        except Exception:
            failed_systems.append("SQLite memory")
        
        # Test Intent classifier
        try:
            intent = self.intent_classifier.classify("what time is it")
            if intent != "time":
                failed_systems.append("intent classifier")
        except Exception:
            failed_systems.append("intent classifier")
        
        # Report results
        if failed_systems:
            self.tts.speak(f"System check failed: {', '.join(failed_systems)} not operational.")
        else:
            self.tts.speak("All systems operational. Memory, voice, and intelligence are online.")
    
    def run(self):
        """Main assistant loop."""
        print("Jarvis is listening...")
        
        while True:
            if self.wake_detector.detect():
                if self.sleeping:
                    self.sleeping = False
                    self.tts.speak("I'm back online. How can I help you?")
                    continue
                
                self.tts.speak("Yes, how can I help you?")
                
                command = self.stt.listen()
                if command:
                    command_lower = command.lower()
                    
                    # Check for sleep commands
                    if "go to sleep" in command_lower or "stop listening" in command_lower:
                        self.sleeping = True
                        self.tts.speak("Going into standby mode.")
                        continue
                    
                    # Check for exit commands
                    if "exit" in command_lower or "shutdown jarvis" in command_lower:
                        self.tts.speak("Goodbye! Shutting down Jarvis.")
                        break
                    
                    # Check for PC control commands
                    if command_lower.startswith("type "):
                        text_to_type = command[5:].strip()  # Remove "type " prefix
                        response = pc_control.type_text(text_to_type)
                        
                        response = self.personality.apply_style(response)
                        self.tts.speak(response)
                        self.memory.add(command, response)
                        self.persistent_memory.save(command, response)
                        continue
                    
                    if command_lower.startswith("press "):
                        key_to_press = command[6:].strip()  # Remove "press " prefix
                        response = pc_control.press_key(key_to_press)
                        
                        response = self.personality.apply_style(response)
                        self.tts.speak(response)
                        self.memory.add(command, response)
                        self.persistent_memory.save(command, response)
                        continue
                    
                    if command_lower.startswith("open "):
                        app_to_open = command[5:].strip()  # Remove "open " prefix
                        response = pc_control.open_app(app_to_open)
                        
                        response = self.personality.apply_style(response)
                        self.tts.speak(response)
                        self.memory.add(command, response)
                        self.persistent_memory.save(command, response)
                        continue
                    
                    # Check for goals management commands
                    if "remember my goal:" in command_lower:
                        goal_text = command_lower.split("remember my goal:", 1)[1].strip()
                        self.goals_manager.add_goal(goal_text)
                        response = f"I've added your goal: {goal_text}"
                        
                        response = self.personality.apply_style(response)
                        self.tts.speak(response)
                        self.memory.add(command, response)
                        self.persistent_memory.save(command, response)
                        continue
                    
                    if "what are my goals" in command_lower:
                        goals = self.goals_manager.list_goals()
                        if goals:
                            response = "Your active goals are: " + ", ".join(goals)
                        else:
                            response = "You have no active goals."
                        
                        response = self.personality.apply_style(response)
                        self.tts.speak(response)
                        self.memory.add(command, response)
                        self.persistent_memory.save(command, response)
                        continue
                    
                    if "mark goal" in command_lower and "as done" in command_lower:
                        # Extract goal ID
                        import re
                        match = re.search(r'mark goal (\d+) as done', command_lower)
                        if match:
                            goal_id = int(match.group(1))
                            self.goals_manager.mark_done(goal_id)
                            response = f"Goal {goal_id} marked as completed."
                        else:
                            response = "Please specify the goal ID to mark as done."
                        
                        response = self.personality.apply_style(response)
                        self.tts.speak(response)
                        self.memory.add(command, response)
                        self.persistent_memory.save(command, response)
                        continue
                    
                    # Check for agent mode commands
                    if "enter agent mode" in command_lower:
                        self.tts.speak("Agent mode activated. What task would you like me to complete?")
                        
                        # Listen for the task
                        task_command = self.stt.listen()
                        if task_command:
                            agent = AgentMode(self.tts, self.memory, self.persistent_memory)
                            agent.run_task(task_command)
                        continue
                    
                    if "complete this task:" in command_lower:
                        task = command_lower.split("complete this task:", 1)[1].strip()
                        agent = AgentMode(self.tts, self.memory, self.persistent_memory)
                        agent.run_task(task)
                        continue
                    
                    # Check for code generation commands
                    if ("write code for" in command_lower or "generate code for" in command_lower):
                        # Extract task from command
                        if "write code for" in command_lower:
                            task = command_lower.split("write code for", 1)[1].strip()
                        else:
                            task = command_lower.split("generate code for", 1)[1].strip()
                        
                        self.self_coder.generate_code(task)
                        response = "I've generated the code for you, Sulekh."
                        
                        response = self.personality.apply_style(response)
                        self.tts.speak(response)
                        self.memory.add(command, response)
                        self.persistent_memory.save(command, response)
                        continue
                    
                    # Check for file search commands
                    if ("find file" in command_lower or "search file" in command_lower):
                        # Extract filename from command
                        if "find file" in command_lower:
                            query = command_lower.split("find file", 1)[1].strip()
                        else:
                            query = command_lower.split("search file", 1)[1].strip()
                        
                        matches = self.file_indexer.search(query)
                        
                        if matches:
                            response = f"Found {len(matches)} matches:\n"
                            for i, path in enumerate(matches[:3], 1):
                                filename = os.path.basename(path)
                                response += f"{i}. {filename}\n"
                        else:
                            response = "I couldn't find any matching files."
                        
                        response = self.personality.apply_style(response)
                        self.tts.speak(response)
                        self.memory.add(command, response)
                        self.persistent_memory.save(command, response)
                        continue
                    
                    # Check for repeat commands
                    if "repeat that" in command_lower or "do that again" in command_lower:
                        if self.last_command:
                            command = self.last_command
                        else:
                            response = "There is no previous command to repeat."
                            response = self.personality.apply_style(response)
                            self.tts.speak(response)
                            continue
                    
                    # Check for personality mode switches
                    if "switch to" in command_lower and "mode" in command_lower:
                        if "normal mode" in command_lower:
                            self.personality.set_mode("normal")
                            response = "Switched to normal mode."
                        elif "boss mode" in command_lower:
                            self.personality.set_mode("boss")
                            response = "Boss mode activated."
                        elif "fun mode" in command_lower:
                            self.personality.set_mode("fun")
                            response = "Fun mode activated!"
                        elif "savage mode" in command_lower:
                            self.personality.set_mode("savage")
                            response = "Savage mode engaged."
                        else:
                            response = "Unknown mode. Available modes: normal, boss, fun, savage."
                        
                        response = self.personality.apply_style(response)
                        self.tts.speak(response)
                        self.memory.add(command, response)
                        self.persistent_memory.save(command, response)
                        continue
                    
                    # Check for diagnostics commands
                    if "run diagnostics" in command_lower or "system check" in command_lower:
                        self._run_diagnostics()
                        continue
                    
                    # Classify intent and route accordingly
                    intent = self.intent_classifier.classify(command)
                    
                    if intent == "time":
                        response = get_time_date()
                    elif intent == "system":
                        response = open_app(command)
                    elif intent == "search":
                        response = search_web(command)
                    else:  # intent == "chat"
                        context = self._get_combined_context()
                        response = self.llm.generate_reply(command, context)
                        
                        # Check if Gemini is uncertain and verify with web search
                        if any(phrase in response.lower() for phrase in ["i think", "i'm not sure", "possibly", "might be"]):
                            self.tts.speak("Let me verify that for you.")
                            response = search_web(command)
                    
                    # Store successful command for repeat functionality
                    if "repeat that" not in command_lower and "do that again" not in command_lower:
                        self.last_command = command
                    
                    # Auto-adjust personality every 10 interactions
                    self.personality.interaction_count += 1
                    if self.personality.interaction_count % 10 == 0:
                        context = self._get_combined_context()
                        self.personality.auto_adjust_mode(context)
                    
                    # Apply personality style to response
                    response = self.personality.apply_style(response)
                    
                    self.tts.speak(response)
                    self.memory.add(command, response)
                    self.persistent_memory.save(command, response)