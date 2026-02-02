"""Gemini LLM implementation using google.generativeai."""

import google.generativeai as genai
from config import GEMINI_API_KEY

class GeminiLLM:
    """Gemini AI language model wrapper for generating responses."""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_reply(self, prompt: str, context: str = "") -> str:
        """Generate a reply using Gemini AI."""
        try:
            full_prompt = f"{context}\n{prompt}" if context else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        except (ValueError, ConnectionError, TimeoutError) as e:
            return f"Error generating reply: {str(e)}"
