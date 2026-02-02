"""Enhanced entertainment skill with multiple free APIs."""

import random
from core.api_manager import SyncAPIManager
from loguru import logger

class EntertainmentSkill:
    """Provides entertainment features using free APIs."""

    def __init__(self):
        self.api_manager = SyncAPIManager()
        self.commands = {
            "quote": ["quote", "inspiration", "motivate", "inspire me"],
            "joke": ["joke", "funny", "make me laugh", "tell me a joke"],
            "fact": ["fact", "interesting fact", "random fact", "tell me something interesting"],
            "advice": ["advice", "tip", "suggestion", "help me decide"],
            "cat_fact": ["cat fact", "cat", "kitty", "feline"],
            "dog_image": ["dog", "puppy", "dog picture", "cute dog"],
            "nasa": ["space", "nasa", "astronomy", "space picture"],
            "trivia": ["trivia", "quiz", "test me", "brain teaser"]
        }

    def can_handle(self, text: str) -> bool:
        """Check if this skill can handle the request."""
        text_lower = text.lower()
        for command_list in self.commands.values():
            if any(cmd in text_lower for cmd in command_list):
                return True
        return False

    def execute(self, text: str) -> str:
        """Execute entertainment command."""
        text_lower = text.lower()

        try:
            # Quote requests
            if any(cmd in text_lower for cmd in self.commands["quote"]):
                return self._get_quote()

            # Joke requests
            elif any(cmd in text_lower for cmd in self.commands["joke"]):
                return self._get_joke()

            # Fact requests
            elif any(cmd in text_lower for cmd in self.commands["fact"]):
                return self._get_fact()

            # Advice requests
            elif any(cmd in text_lower for cmd in self.commands["advice"]):
                return self._get_advice()

            # Cat fact requests
            elif any(cmd in text_lower for cmd in self.commands["cat_fact"]):
                return self._get_cat_fact()

            # Dog image requests
            elif any(cmd in text_lower for cmd in self.commands["dog_image"]):
                return self._get_dog_image()

            # NASA requests
            elif any(cmd in text_lower for cmd in self.commands["nasa"]):
                return self._get_nasa_info()

            # Trivia requests
            elif any(cmd in text_lower for cmd in self.commands["trivia"]):
                return self._get_trivia()

            else:
                return self._get_random_entertainment()

        except Exception as e:
            logger.error(f"Entertainment skill error: {e}")
            return "Sorry, I'm having trouble with entertainment features right now."

    def _get_quote(self) -> str:
        """Get inspirational quote."""
        try:
            quote_data = self.api_manager.get_random_quote()
            return f"Here's an inspiring quote: \"{quote_data['quote']}\" - {quote_data['author']}"
        except Exception as e:
            logger.error(f"Quote error: {e}")
            return "Here's a quote: 'The only way to do great work is to love what you do.' - Steve Jobs"

    def _get_joke(self) -> str:
        """Get random joke."""
        try:
            joke_data = self.api_manager.get_random_joke()
            return f"{joke_data['setup']} {joke_data['punchline']}"
        except Exception as e:
            logger.error(f"Joke error: {e}")
            return "Why don't scientists trust atoms? Because they make up everything!"

    def _get_fact(self) -> str:
        """Get random fact."""
        try:
            fact = self.api_manager.get_random_fact()
            return f"Here's an interesting fact: {fact}"
        except Exception as e:
            logger.error(f"Fact error: {e}")
            return "Here's a fact: The human brain contains approximately 86 billion neurons."

    def _get_advice(self) -> str:
        """Get random advice."""
        try:
            advice = self.api_manager.get_advice()
            return f"Here's some advice: {advice}"
        except Exception as e:
            logger.error(f"Advice error: {e}")
            return "Here's some advice: Take time to make your soul happy."

    def _get_cat_fact(self) -> str:
        """Get cat fact."""
        try:
            fact = self.api_manager.get_cat_fact()
            return f"Cat fact: {fact}"
        except Exception as e:
            logger.error(f"Cat fact error: {e}")
            return "Cat fact: Cats sleep 12-16 hours per day."

    def _get_dog_image(self) -> str:
        """Get dog image."""
        try:
            image_url = self.api_manager.get_dog_image()
            return f"Here's a cute dog picture: {image_url}"
        except Exception as e:
            logger.error(f"Dog image error: {e}")
            return "I'd show you a cute dog picture, but I'm having trouble accessing the image service right now."

    def _get_nasa_info(self) -> str:
        """Get NASA astronomy picture."""
        try:
            nasa_data = self.api_manager.get_nasa_apod()
            return f"NASA's Astronomy Picture: {nasa_data['title']}. {nasa_data['explanation'][:200]}... View it at: {nasa_data.get('url', 'URL not available')}"
        except Exception as e:
            logger.error(f"NASA error: {e}")
            return "I'm having trouble accessing NASA's astronomy data right now."

    def _get_trivia(self) -> str:
        """Get random trivia."""
        trivia_questions = [
            "What's the largest planet in our solar system? (Answer: Jupiter)",
            "Which element has the chemical symbol 'Au'? (Answer: Gold)",
            "What year did the Berlin Wall fall? (Answer: 1989)",
            "What's the smallest country in the world? (Answer: Vatican City)",
            "Which mammal is known to have the most powerful bite? (Answer: Hippopotamus)"
        ]
        return f"Trivia time! {random.choice(trivia_questions)}"

    def _get_random_entertainment(self) -> str:
        """Get random entertainment content."""
        options = [
            self._get_quote,
            self._get_joke,
            self._get_fact,
            self._get_advice
        ]
        return random.choice(options)()
