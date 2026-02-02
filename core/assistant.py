"""Main Jarvis assistant."""

import json
import os
import re
import threading
import time
import tkinter as tk
from typing import List

from core.gemini_llm import GeminiLLM
from core.intent_classifier import IntentClassifier
from core.life_automation import LifeAutomation
from core.life_os import LifeOS
from core.personality import PersonalityManager
from core.safety import SafetyManager
from core.self_coder import SelfCoder
from core.self_improver import SelfImprover
from core.skill_learner import SkillLearner
from core.skill_manager import SkillManager
from core.speech_to_text import SpeechToText
from core.text_to_speech import TextToSpeech
from core.wake_word_detector import WakeWordDetector
from hud import JarvisOverlay
from utils.file_indexer import FileIndexer
from utils.goals import GoalsManager
from utils.memory import Memory
from utils.persistent_memory import PersistentMemory
from utils.routines import RoutinesManager

class JarvisAssistant:
    """Main Jarvis assistant class that integrates all components."""
    def __init__(self):
        self.stt = SpeechToText()
        self.stt.set_language("auto")  # Enable auto language detection
        self.tts = TextToSpeech()
        self.llm = GeminiLLM()
        self.memory = Memory()
        self.persistent_memory = PersistentMemory()
        self.wake_detector = WakeWordDetector("jarvis")
        self.intent_classifier = IntentClassifier()
        self.personality = PersonalityManager()
        self.self_coder = SelfCoder()
        self.skill_learner = SkillLearner()
        self.life_os = LifeOS()
        self.self_improver = SelfImprover(self.memory, self.persistent_memory)
        self.safety_manager = SafetyManager()
        self.life_automation = LifeAutomation(self.memory, self.persistent_memory)
        self.file_indexer = FileIndexer(root_dir=os.getcwd())
        self.goals_manager = GoalsManager()
        self.routines_manager = RoutinesManager()
        self.skill_manager = SkillManager()
        self.sleeping = False
        self.last_command = None
        self.overlay = None
        self._start_routine_checker()
        self._start_proactive_assistant()
        self._setup_ui()

    def _setup_ui(self):
        """Setup the overlay UI."""
        try:
            # Create hidden root window
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the main window

            # Create overlay
            self.overlay = JarvisOverlay(assistant_callback=self.process_text_command)

            # Start UI in separate thread
            threading.Thread(target=self._run_ui, daemon=True).start()
        except Exception as e:  # pylint: disable=broad-except
            print(f"UI setup failed: {e}")

    def _run_ui(self):
        """Run the UI in a separate thread."""
        try:
            if self.overlay:
                self.overlay.start()
        except Exception as e:  # pylint: disable=broad-except
            print(f"UI error: {e}")

    def process_text_command(self, command: str) -> str:
        """Process text command and return response."""
        try:
            # Check for sleep commands
            if self.wake_detector.is_sleep_command(command):
                if self.overlay:
                    self.overlay.toggle_sleep()
                return "Going into sleep mode. Say 'Jarvis' to wake me up."

            # Check for wake commands when sleeping
            if self.sleeping and self.wake_detector.is_wake_word(command):
                self.sleeping = False
                if self.overlay:
                    self.overlay.wake_up()
                return "I'm back online. How can I help you?"

            # Process normal commands
            if not self.sleeping:
                return self._process_command(command)
            else:
                return "I'm sleeping. Say 'Jarvis' to wake me up."

        except Exception as e:  # pylint: disable=broad-except
            return f"Error processing command: {str(e)}"

    def _process_command(self, command: str) -> str:
        """Process a command and return response."""
        try:
            # Detect language and set context
            is_hindi = self._is_hindi_text(command)
            lang_context = (
                "Respond in Hindi (Devanagari script)" if is_hindi 
                else "Respond in English"
            )

            # Get all skill descriptions
            skill_descriptions = self.skill_manager.get_all_skills_descriptions()

            # Formulate prompt for LLM
            prompt = f"""
            User command: "{command}"
            Language instruction: {lang_context}

            Available skills:
            {skill_descriptions}

            Based on the user's command, which skill should be executed?
            If the command requires arguments, extract them.
            Respond with the skill name and arguments in JSON format, like this:
            {{
                "skill_name": "skill_name",
                "args": ["arg1", "arg2"],
                "kwargs": {{"key1": "value1"}}
            }}
            If no skill matches, respond with:
            {{
                "skill_name": "chat",
                "args": [],
                "kwargs": {{}}
            }}
            """

            llm_response = self.llm.generate_reply(prompt, "")
            try:
                parsed_response = json.loads(llm_response)
            except json.JSONDecodeError:
                # If LLM doesn't return valid JSON, fall back to chat
                parsed_response = {"skill_name": "chat", "args": [], "kwargs": {}}

            skill_name = parsed_response.get("skill_name")
            args = parsed_response.get("args", [])
            kwargs = parsed_response.get("kwargs", {})

            if skill_name and skill_name != "chat":
                response = self.skill_manager.execute_skill(skill_name, *args, **kwargs)
            else:
                context = self._get_combined_context()
                chat_prompt = f"{lang_context}. User: {command}"
                response = self.llm.generate_reply(chat_prompt, context)

        except Exception as e:  # pylint: disable=broad-except
            print(f"Error processing command: {e}")
            context = self._get_combined_context()
            is_hindi = self._is_hindi_text(command)
            lang_context = (
                "Respond in Hindi (Devanagari script)" if is_hindi 
                else "Respond in English"
            )
            chat_prompt = f"{lang_context}. User: {command}"
            response = self.llm.generate_reply(chat_prompt, context)

        # Apply personality style to response
        response = self.personality.apply_style(response)

        # Save to memory
        self.memory.add(command, response)
        self.persistent_memory.save(command, response)

        return response

    def _is_hindi_text(self, text: str) -> bool:
        """Check if text contains Hindi characters."""
        hindi_chars = re.findall(r'[ऀ-ॿ]', text)
        return len(hindi_chars) > 0

    def _get_combined_context(self) -> str:
        """Get combined context from persistent and short-term memory."""
        # Get persistent memory
        persistent = self.persistent_memory.fetch_last(5)
        persistent_context = "\n".join(
            [f"User: {user}\nJarvis: {jarvis}" for user, jarvis in persistent]
        )

        # Get short-term memory
        short_term_context = self.memory.get_context()

        # Combine contexts
        combined = (
            f"{persistent_context}\n{short_term_context}" 
            if persistent_context else short_term_context
        )

        # Trim to 2000 characters from oldest side
        if len(combined) > 2000:
            combined = combined[-2000:]

        return combined

    def _run_diagnostics(self):
        """Run system diagnostics and report status."""
        failed_systems: List[str] = []

        # Test TTS
        try:
            self.tts.speak("Testing voice system.")
        except Exception:  # pylint: disable=broad-except
            failed_systems.append("voice system")

        # Test Gemini API
        try:
            response = self.llm.generate_reply("Reply with: Gemini OK", "")
            if "OK" not in response:
                failed_systems.append("Gemini API")
        except Exception:  # pylint: disable=broad-except
            failed_systems.append("Gemini API")

        # Test SQLite memory
        try:
            self.persistent_memory.save("test_user", "test_jarvis")
            last_interactions = self.persistent_memory.fetch_last(1)
            if not last_interactions or last_interactions[0][0] != "test_user":
                failed_systems.append("SQLite memory")
        except Exception:  # pylint: disable=broad-except
            failed_systems.append("SQLite memory")

        # Test Intent classifier
        try:
            intent = self.intent_classifier.classify("what time is it")
            if intent != "time":
                failed_systems.append("intent classifier")
        except Exception:  # pylint: disable=broad-except
            failed_systems.append("intent classifier")

        # Report results
        if failed_systems:
            self.tts.speak(
                f"System check failed: {', '.join(failed_systems)} not operational."
            )
        else:
            self.tts.speak(
                "All systems operational. Memory, voice, and intelligence are online."
            )

    def _start_routine_checker(self):
        """Start background thread to check for due routines."""

        def check_routines():
            while True:
                try:
                    due_tasks = self.routines_manager.check_due_tasks()
                    for task in due_tasks:
                        self.tts.speak(f"Routine reminder: {task}")
                except Exception:  # pylint: disable=broad-except
                    pass
                time.sleep(60)  # Check every 60 seconds

        routine_thread = threading.Thread(
            target=check_routines, daemon=True
        )
        routine_thread.start()

    def _start_proactive_assistant(self):
        """Start background thread for proactive assistance."""

        def proactive_check():
            while True:
                try:
                    time.sleep(1800)  # Wait 30 minutes
                    if not self.sleeping:  # Only suggest when awake
                        suggestion = self.life_automation.proactive_assist()
                        if suggestion:
                            self.tts.speak(suggestion)
                except Exception:  # pylint: disable=broad-except
                    pass

        proactive_thread = threading.Thread(
            target=proactive_check, daemon=True
        )
        proactive_thread.start()

    def run(self):
        """Main assistant loop with voice and UI support."""
        print("Jarvis is listening...")

        # Start voice listening in background
        voice_thread = threading.Thread(
            target=self._voice_loop, daemon=True
        )
        voice_thread.start()

        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down Jarvis...")

    def _voice_loop(self):
        """Voice recognition loop."""

        while True:
            try:
                if (
                    not self.sleeping and self.overlay and self.overlay.is_enabled
                ):
                    if self.wake_detector.detect():
                        # Check if overlay is sleeping
                        if self.overlay.is_sleeping:
                            continue

                        if self.overlay:
                            self.overlay.set_listening(True)

                        self.tts.speak("Yes, how can I help you?")

                        command = self.stt.listen()
                        if command:
                            # Check for wake word
                            if self.wake_detector.is_wake_word(command):
                                if self.overlay and self.overlay.is_sleeping:
                                    self.overlay.wake_up()
                                    self.tts.speak(
                                        "I'm back online. How can I help you?"
                                    )
                                    continue

                            # Process command
                            response = self.process_text_command(command)
                            self.tts.speak(response)

                            # Update UI
                            if self.overlay:
                                self.overlay.add_message("You (Voice)", command)
                                self.overlay.add_message("JARVIS", response)

                        if self.overlay:
                            self.overlay.set_listening(False)

                time.sleep(0.1)  # Small delay to prevent high CPU usage

            except Exception as e:  # pylint: disable=broad-except
                print(f"Voice loop error: {e}")
                time.sleep(1)