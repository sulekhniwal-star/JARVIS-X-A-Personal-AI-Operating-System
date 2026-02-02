from typing import Any
from duckduckgo_search import DDGS  # type: ignore


def search_web(query: str) -> str:
    """Search web using DuckDuckGo and return formatted results."""
    try:
        with DDGS(timeout=5) as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            return "I couldn't find reliable results right now."

        formatted = "Here's what I found:\n"
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('body', 'No description')
            formatted += f"{i}) {title} – {snippet}\n"

        return formatted.strip()

    except Exception:
        return "I couldn't find reliable results right now."
