import os
import importlib.util
from core.gemini_llm import GeminiLLM


class SkillLearner:
    def __init__(self):
        self.llm = GeminiLLM()
    
    def learn_skill(self, name: str, description: str) -> str:
        """Generate and save a new skill module."""
        try:
            # Generate skill code using Gemini
            prompt = f"""Write a Python skill module named {name}.
It must expose a function run(text: str) -> str.
It must be safe, deterministic, and not destructive.
Description: {description}

Only return the Python code, no explanations."""
            
            code = self.llm.generate_reply(prompt, "")
            
            # Clean up code (remove markdown if present)
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]
            
            # Save to skills directory
            skill_path = f"skills/{name}.py"
            with open(skill_path, "w", encoding="utf-8") as f:
                f.write(code.strip())
            
            # Validate the skill
            if self._validate_skill(skill_path):
                return f"New skill '{name}' learned successfully."
            else:
                os.remove(skill_path)  # Remove invalid skill
                return f"Failed to learn skill '{name}'. Generated code was invalid."
        
        except Exception:
            return f"Failed to learn skill '{name}' due to an error."
    
    def _validate_skill(self, skill_path: str) -> bool:
        """Validate that the skill module is valid and has run() function."""
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location("temp_skill", skill_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if run function exists and is callable
            if hasattr(module, 'run') and callable(getattr(module, 'run')):
                return True
            
            return False
        
        except Exception:
            return False