from typing import List

from .base_structure import BaseStructure
from ..template import Template


class BotStructure(BaseStructure):
    name = "bot"
    schema: List[Template] = [
        Template(base_directory="bot", target_file="main.py"),
        Template(base_directory="bot", target_file="__init__.py"),
        Template(base_directory="bot/handlers", target_file="__init__.py"),
        Template(base_directory=".", target_file=".gitignore"),
        Template(base_directory="settings", target_file="__init__.py"),
        Template(base_directory="settings", target_file="settings.py")
        ]


