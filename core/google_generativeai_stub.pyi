"""Type stubs for google.generativeai package."""
# pylint: disable=unused-argument,missing-docstring

from typing import Optional

def configure(api_key: str) -> None: ...

class GenerativeModel:
    def __init__(self, model_name: str, system_instruction: Optional[str] = None) -> None: ...
    def generate_content(self, prompt: str) -> "GenerateContentResponse": ...

class GenerateContentResponse:
    @property
    def text(self) -> str: ...
