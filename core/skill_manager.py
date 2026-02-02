import importlib
import inspect
import os
from typing import Dict, Any, List

class SkillManager:
    """
    Dynamically loads skills from the 'skills' directory.
    """
    def __init__(self, skills_directory="skills"):
        self.skills_directory = skills_directory
        self.skills: Dict[str, Any] = {}
        self.load_skills()

    def load_skills(self):
        """
        Loads all skills from the skills directory.
        """
        if not os.path.exists(self.skills_directory):
            print(f"Skills directory '{self.skills_directory}' not found.")
            return

        for filename in os.listdir(self.skills_directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = f"{self.skills_directory}.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for attribute_name in dir(module):
                        attribute = getattr(module, attribute_name)
                        if inspect.isfunction(attribute) and not attribute_name.startswith("__"):
                            # We'll use the function name as the skill name
                            self.skills[attribute_name] = {
                                "function": attribute,
                                "docstring": inspect.getdoc(attribute)
                            }
                except ImportError as e:
                    print(f"Error importing skill from {filename}: {e}")

    def get_all_skills_descriptions(self) -> List[str]:
        """
        Returns a list of all skill descriptions.
        """
        descriptions = []
        for skill_name, skill_data in self.skills.items():
            if skill_data['docstring']:
                descriptions.append(f"- {skill_name}: {skill_data['docstring']}")
        return descriptions

    def execute_skill(self, skill_name: str, *args, **kwargs) -> Any:
        """
        Executes a skill by name.
        """
        if skill_name in self.skills:
            try:
                return self.skills[skill_name]["function"](*args, **kwargs)
            except Exception as e:
                print(f"Error executing skill '{skill_name}': {e}")
                raise
        else:
            return f"Skill '{skill_name}' not found."

