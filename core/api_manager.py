"""Enhanced API Manager for JARVIS-X with multiple free APIs."""

import asyncio
from typing import Any, Dict, List
import aiohttp
from aiohttp import ClientError, ClientTimeout

from core.config import FREE_APIS, NEWS_API_KEY, WEATHER_API_KEY

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

class APIManager:
    """Manages all external API integrations."""

    def __init__(self):
        if aiohttp is None:
            raise ImportError("aiohttp is required. Install with: pip install aiohttp==3.9.1")
        
        # Set a global timeout for all requests to prevent hanging
        timeout = ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(timeout=timeout)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    # Entertainment APIs
    async def get_random_quote(self) -> Dict[str, Any]:
        """Get inspirational quote."""
        try:
            async with self.session.get(FREE_APIS["quotes"]) as response:
                response.raise_for_status()
                data = await response.json()
                return {"quote": data["content"], "author": data["author"]}
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("Quote API connection error: %s", e)
        except KeyError as e:
            logger.error("Quote API format error: %s", e)
        
        return {
            "quote": "The only way to do great work is to love what you do.",
            "author": "Steve Jobs"
        }

    async def get_random_joke(self) -> Dict[str, Any]:
        """Get random joke."""
        try:
            async with self.session.get(FREE_APIS["jokes"]) as response:
                response.raise_for_status()
                data = await response.json()
                return {"setup": data["setup"], "punchline": data["punchline"]}
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("Joke API connection error: %s", e)
        except KeyError as e:
            logger.error("Joke API format error: %s", e)

        return {
            "setup": "Why don't scientists trust atoms?",
            "punchline": "Because they make up everything!"
        }

    async def get_random_fact(self) -> str:
        """Get random interesting fact."""
        try:
            async with self.session.get(FREE_APIS["facts"]) as response:
                response.raise_for_status()
                data = await response.json()
                return data["text"]
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("Facts API connection error: %s", e)
        except KeyError as e:
            logger.error("Facts API format error: %s", e)

        return "The human brain contains approximately 86 billion neurons."

    async def get_advice(self) -> str:
        """Get random advice."""
        try:
            async with self.session.get(FREE_APIS["advice"]) as response:
                response.raise_for_status()
                data = await response.json()
                return data["slip"]["advice"]
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("Advice API connection error: %s", e)
        except KeyError as e:
            logger.error("Advice API format error: %s", e)

        return "Take time to make your soul happy."

    # Information APIs
    async def get_crypto_price(self, crypto: str = "bitcoin") -> Dict[str, Any]:
        """Get cryptocurrency price."""
        try:
            url = f"{FREE_APIS['crypto']}?ids={crypto}&vs_currencies=usd"
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return {crypto: data[crypto]["usd"]}
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("Crypto API connection error: %s", e)
        except KeyError as e:
            logger.error("Crypto API format error: %s", e)

        return {crypto: "Price unavailable"}

    async def get_exchange_rates(self) -> Dict[str, Any]:
        """Get currency exchange rates."""
        try:
            url = f"{FREE_APIS['exchange']}"
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return {"base": data["base"], "rates": data["rates"]}
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("Exchange API connection error: %s", e)
        except KeyError as e:
            logger.error("Exchange API format error: %s", e)

        return {"base": "USD", "rates": {}}

    async def get_ip_info(self) -> Dict[str, Any]:
        """Get current IP information."""
        try:
            async with self.session.get(FREE_APIS["ip_info"]) as response:
                response.raise_for_status()
                data = await response.json()
                return {
                    "ip": data.get("ip", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "country": data.get("country_name", "Unknown"),
                    "timezone": data.get("timezone", "Unknown")
                }
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("IP Info API connection error: %s", e)
        
        return {"ip": "Unknown", "city": "Unknown", "country": "Unknown"}

    # News API
    async def get_news(self, category: str = "technology", country: str = "us") -> List[Dict]:
        """Get latest news."""
        if not NEWS_API_KEY:
            return [{
                "title": "News API key not configured",
                "description": "Please add NEWS_API_KEY to .env"
            }]

        try:
            url = (
                f"https://newsapi.org/v2/top-headlines?"
                f"country={country}&category={category}&apiKey={NEWS_API_KEY}"
            )
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("articles", [])[:5]  # Return top 5 articles
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("News API connection error: %s", e)
        except KeyError as e:
            logger.error("News API format error: %s", e)

        return [{"title": "News unavailable", "description": "Error fetching news"}]

    # Weather API
    async def get_weather(self, city: str = "London") -> Dict[str, Any]:
        """Get weather information."""
        if not WEATHER_API_KEY:
            return {"error": "Weather API key not configured"}

        try:
            url = (
                f"http://api.openweathermap.org/data/2.5/weather?"
                f"q={city}&appid={WEATHER_API_KEY}&units=metric"
            )
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return {
                    "city": data["name"],
                    "temperature": data["main"]["temp"],
                    "description": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"]
                }
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("Weather API connection error: %s", e)
        except KeyError as e:
            logger.error("Weather API format error: %s", e)

        return {"error": "Weather data unavailable"}

    # Fun APIs
    async def get_cat_fact(self) -> str:
        """Get random cat fact."""
        try:
            async with self.session.get(FREE_APIS["cat_facts"]) as response:
                response.raise_for_status()
                data = await response.json()
                return data["fact"]
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("Cat Facts API connection error: %s", e)
        except KeyError as e:
            logger.error("Cat Facts API format error: %s", e)

        return "Cats sleep 12-16 hours per day."

    async def get_dog_image(self) -> str:
        """Get random dog image URL."""
        try:
            async with self.session.get(FREE_APIS["dog_images"]) as response:
                response.raise_for_status()
                data = await response.json()
                return data["message"]
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("Dog Images API connection error: %s", e)
        except KeyError as e:
            logger.error("Dog Images API format error: %s", e)

        return "https://images.dog.ceo/breeds/retriever-golden/n02099601_100.jpg"

    # NASA API
    async def get_nasa_apod(self) -> Dict[str, Any]:
        """Get NASA Astronomy Picture of the Day."""
        try:
            url = f"{FREE_APIS['nasa_apod']}?api_key=DEMO_KEY"
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return {
                    "title": data.get("title", "Unknown"),
                    "explanation": data.get("explanation", "No description available"),
                    "url": data.get("url", ""),
                    "date": data.get("date", "Unknown")
                }
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("NASA API connection error: %s", e)
        except KeyError as e:
            logger.error("NASA API format error: %s", e)

        return {"title": "Space Image Unavailable", "explanation": "Error fetching NASA data"}

    # Dictionary API
    async def get_word_definition(self, word: str) -> Dict[str, Any]:
        """Get word definition."""
        try:
            url = f"{FREE_APIS['dictionary']}/{word}"
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                if isinstance(data, list) and len(data) > 0:
                    meanings = data[0].get("meanings", [])
                    if meanings:
                        definition = (
                            meanings[0].get("definitions", [{}])[0]
                            .get("definition", "No definition found")
                        )
                        return {"word": word, "definition": definition}
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("Dictionary API connection error: %s", e)
        except KeyError as e:
            logger.error("Dictionary API format error: %s", e)

        return {"word": word, "definition": "Definition not found"}

    # GitHub API
    async def get_github_user(self, username: str) -> Dict[str, Any]:
        """Get GitHub user information."""
        try:
            url = f"https://api.github.com/users/{username}"
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return {
                    "username": data.get("login", "Unknown"),
                    "name": data.get("name", "Unknown"),
                    "bio": data.get("bio", "No bio available"),
                    "public_repos": data.get("public_repos", 0),
                    "followers": data.get("followers", 0)
                }
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error("GitHub API connection error: %s", e)
        except KeyError as e:
            logger.error("GitHub API format error: %s", e)

        return {"username": username, "error": "User information not found"}