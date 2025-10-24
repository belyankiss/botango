from typing import Dict, Any, List

from .template import Template


class BotStructure:
    """
    Класс, описывающий структуру проекта бота.

    Содержит схему файлов, создаваемых из шаблонов.
    """
    def __init__(self, data: Dict[str, Any] = None):
        self.data = data or {}
        # Базовые данные, которые доступны в шаблонах
        default_data = {
            "name_project": "bot"
        } | self.data

        # Схема проекта — список шаблонов, которые нужно создать
        self.schema: List[Template] = [
            Template(base_directory="bot", target_file="main.py", data=default_data),
            Template(base_directory="bot", target_file="__init__.py", data=default_data),
            Template(base_directory="bot/handlers", target_file="__init__.py", data=default_data)
        ]

    def build_project(self):
        """
        Создаёт все файлы, указанные в схеме проекта.
        """
        for value in self.schema:
            value.create()

    def add_template(self, template: Template):
        """
        Добавляет новый шаблон в проект.
        Можно использовать для динамического расширения схемы.
        """
        self.schema.append(template)


