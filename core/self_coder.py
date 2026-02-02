"""Self-coding module for JARVIS-X autonomous code generation."""
from core.gemini_llm import GeminiLLM


class SelfCoder:
    """Autonomous code generation system for JARVIS-X."""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.llm = GeminiLLM()
        self.system_prompt = (
            "You are Jarvis, an elite software engineer. "
            "Write clean, modular Python code."
        )

    def generate_code(self, task: str) -> str:
        """Generate Python code for the given task."""
        try:
            # Generate code using Gemini
            full_prompt = f"{self.system_prompt}\n\nTask: {task}"
            code = self.llm.generate_reply(full_prompt, "")

            # Save to file
            with open("generated_code.py", "w", encoding="utf-8") as f:
                f.write(code)

            return code

        except (OSError, IOError, ValueError):
            return "# Error generating code"
