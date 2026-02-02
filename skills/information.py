"""Enhanced information skill with multiple free APIs."""

import re
from loguru import logger
from core.api_manager import SyncAPIManager

class InformationSkill:
    """Provides information using various free APIs."""

    def __init__(self):
        self.api_manager = SyncAPIManager()
        self.commands = {
            "weather": ["weather", "temperature", "forecast", "climate"],
            "news": ["news", "headlines", "latest news", "current events"],
            "crypto": ["bitcoin", "cryptocurrency", "crypto", "btc", "eth",
                       "ethereum"],
            "exchange": ["exchange rate", "currency", "dollar", "euro",
                         "conversion"],
            "definition": ["define", "meaning", "what is", "definition of"],
            "ip": ["my ip", "ip address", "location", "where am i"],
            "github": ["github", "git profile", "repository", "repos"]
        }

    def can_handle(self, text: str) -> bool:
        """Check if this skill can handle the request."""
        text_lower = text.lower()
        for command_list in self.commands.values():
            if any(cmd in text_lower for cmd in command_list):
                return True
        return False

    def execute(self, text: str) -> str:
        """Execute information command."""
        text_lower = text.lower()

        try:
            # Weather requests
            if any(cmd in text_lower for cmd in self.commands["weather"]):
                return self._get_weather(text)

            # News requests
            elif any(cmd in text_lower for cmd in self.commands["news"]):
                return self._get_news(text)

            # Crypto requests
            elif any(cmd in text_lower for cmd in self.commands["crypto"]):
                return self._get_crypto_info(text)

            # Exchange rate requests
            elif any(cmd in text_lower for cmd in self.commands["exchange"]):
                return self._get_exchange_rates()

            # Definition requests
            elif any(cmd in text_lower for cmd in self.commands["definition"]):
                return self._get_definition(text)

            # IP information requests
            elif any(cmd in text_lower for cmd in self.commands["ip"]):
                return self._get_ip_info()

            # GitHub requests
            elif any(cmd in text_lower for cmd in self.commands["github"]):
                return self._get_github_info(text)

            else:
                return "I can help you with weather, news, cryptocurrency prices, definitions, and more!"

        except Exception as e:
            logger.error(f"Information skill error: {e}")
            return "Sorry, I'm having trouble accessing information services right now."

    def _get_weather(self, text: str) -> str:
        """Get weather information."""
        try:
            # Extract city from text
            city = self._extract_city(text)
            weather_data = self.api_manager.get_weather(city)

            if "error" in weather_data:
                return f"Sorry, I couldn't get weather information for {city}. Please check the city name."

            return (f"Weather in {weather_data['city']}: "
                    f"{weather_data['temperature']}°C, {weather_data['description']}. "
                    f"Humidity: {weather_data['humidity']}%, "
                    f"Wind: {weather_data['wind_speed']} m/s")
        except Exception as e:
            logger.error(f"Weather error: {e}")
            return "I'm having trouble getting weather information right now."

    def _get_news(self, text: str) -> str:
        """Get latest news."""
        try:
            # Extract category if mentioned
            category = self._extract_news_category(text)
            news_articles = self.api_manager.get_news(category)

            if not news_articles or "error" in str(news_articles):
                return "I'm having trouble accessing news right now. Please make sure NEWS_API_KEY is configured."

            response = f"Here are the latest {category} headlines:\\n\\n"
            for i, article in enumerate(news_articles[:3], 1):
                title = article.get("title", "No title")
                description = article.get("description", "No description")[:100]
                response += f"{i}. {title}\\n   {description}...\\n\\n"

            return response
        except Exception as e:
            logger.error(f"News error: {e}")
            return "I'm having trouble getting news right now."

    def _get_crypto_info(self, text: str) -> str:
        """Get cryptocurrency information."""
        try:
            # Extract crypto name
            crypto = self._extract_crypto(text)
            price_data = self.api_manager.get_crypto_price(crypto)

            if crypto in price_data:
                price = price_data[crypto]
                return f"Current {crypto.title()} price: ${price:,.2f} USD"
            else:
                return f"Sorry, I couldn't get price information for {crypto}."
        except Exception as e:
            logger.error(f"Crypto error: {e}")
            return "I'm having trouble getting cryptocurrency prices right now."

    def _get_exchange_rates(self) -> str:
        """Get currency exchange rates."""
        try:
            rates_data = self.api_manager.get_exchange_rates()
            rates = rates_data.get("rates", {})

            if not rates:
                return "I'm having trouble getting exchange rates right now."

            major_currencies = ["EUR", "GBP", "JPY", "CAD", "AUD"]
            response = "Current exchange rates (USD base):\\n"

            for currency in major_currencies:
                if currency in rates:
                    response += f"1 USD = {rates[currency]:.4f} {currency}\\n"

            return response
        except Exception as e:
            logger.error(f"Exchange rates error: {e}")
            return "I'm having trouble getting exchange rates right now."

    def _get_definition(self, text: str) -> str:
        """Get word definition."""
        try:
            # Extract word to define
            word = self._extract_word_to_define(text)
            if not word:
                return "Please specify a word you'd like me to define."

            definition_data = self.api_manager.get_word_definition(word)

            if "error" in definition_data or not definition_data.get("definition"):
                return f"Sorry, I couldn't find a definition for '{word}'."

            return f"Definition of '{word}': {definition_data['definition']}"
        except Exception as e:
            logger.error(f"Definition error: {e}")
            return "I'm having trouble accessing the dictionary right now."

    def _get_ip_info(self) -> str:
        """Get IP and location information."""
        try:
            ip_data = self.api_manager.get_ip_info()

            return (f"Your IP information:\\n"
                    f"IP Address: {ip_data.get('ip', 'Unknown')}\\n"
                    f"Location: {ip_data.get('city', 'Unknown')}, "
                    f"{ip_data.get('country', 'Unknown')}\\n"
                    f"Timezone: {ip_data.get('timezone', 'Unknown')}")
        except Exception as e:
            logger.error(f"IP info error: {e}")
            return "I'm having trouble getting your IP information right now."

    def _get_github_info(self, text: str) -> str:
        """Get GitHub user information."""
        try:
            username = self._extract_github_username(text)
            if not username:
                return "Please specify a GitHub username to look up."

            github_data = self.api_manager.get_github_user(username)

            if "error" in github_data:
                return f"Sorry, I couldn't find GitHub user '{username}'."

            return (f"GitHub user {username}:\\n"
                    f"Name: {github_data.get('name', 'Not provided')}\\n"
                    f"Bio: {github_data.get('bio', 'No bio available')}\\n"
                    f"Public Repos: {github_data.get('public_repos', 0)}\\n"
                    f"Followers: {github_data.get('followers', 0)}\\n"
                    f"Following: {github_data.get('following', 0)}")
        except Exception as e:
            logger.error(f"GitHub error: {e}")
            return "I'm having trouble accessing GitHub information right now."

    # Helper methods for text extraction
    def _extract_city(self, text: str) -> str:
        """Extract city name from text."""
        # Look for patterns like "weather in London" or "London weather"
        patterns = [
            r"weather in ([a-zA-Z\\s]+)",
            r"([a-zA-Z\\s]+) weather",
            r"temperature in ([a-zA-Z\\s]+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "London"  # Default city

    def _extract_news_category(self, text: str) -> str:
        """Extract news category from text."""
        categories = {
            "tech": ["technology", "tech", "ai", "computer"],
            "business": ["business", "finance", "economy", "market"],
            "sports": ["sports", "football", "basketball", "soccer"],
            "health": ["health", "medical", "medicine", "covid"],
            "science": ["science", "research", "study", "discovery"],
            "entertainment": ["entertainment", "movie", "celebrity", "music"]
        }

        text_lower = text.lower()
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category

        return "technology"  # Default category

    def _extract_crypto(self, text: str) -> str:
        """Extract cryptocurrency name from text."""
        crypto_map = {
            "bitcoin": ["bitcoin", "btc"],
            "ethereum": ["ethereum", "eth"],
            "cardano": ["cardano", "ada"],
            "polkadot": ["polkadot", "dot"],
            "chainlink": ["chainlink", "link"]
        }

        text_lower = text.lower()
        for crypto, keywords in crypto_map.items():
            if any(keyword in text_lower for keyword in keywords):
                return crypto

        return "bitcoin"  # Default crypto

    def _extract_word_to_define(self, text: str) -> str:
        """Extract word to define from text."""
        patterns = [
            r"define ([a-zA-Z]+)",
            r"meaning of ([a-zA-Z]+)",
            r"what is ([a-zA-Z]+)",
            r"definition of ([a-zA-Z]+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_github_username(self, text: str) -> str:
        """Extract GitHub username from text."""
        patterns = [
            r"github user ([a-zA-Z0-9\\-_]+)",
            r"github profile ([a-zA-Z0-9\\-_]+)",
            r"github ([a-zA-Z0-9\\-_]+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""
