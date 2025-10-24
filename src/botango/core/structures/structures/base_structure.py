from typing import Dict, Any, List

from botango.core.structures.template import Template


class BaseStructure:
    name: str
    schema: List[Template] = []

    def __init__(self):
        self.data = dict(name_project=self.name)

    def build_project(self, data: Dict[str, Any] = None):
        """
        Создаёт все файлы, указанные в схеме проекта.
        """
        data = data or {}
        self.data = self.data | data
        for tmpl in self.schema:
            tmpl.create(data=self.data)

    def add_template(self, template: Template):
        """
        Добавляет новый шаблон в проект.
        Можно использовать для динамического расширения схемы.
        """
        self.schema.append(template)
