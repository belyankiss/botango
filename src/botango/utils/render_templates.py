from pathlib import Path
from typing import Union

from jinja2 import Environment, FileSystemLoader


class RenderTemplate:
    def __init__(self):
        templates_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(templates_dir), trim_blocks=True, lstrip_blocks=True)

    def _render(self, template: str, *args, **kwargs) -> str:
        template = self.env.get_template(template)
        file = template.render(*args, **kwargs)
        return file

    @staticmethod
    def _make_file(filename: Union[str, Path], rows: str):
        with open(filename, "w", encoding="utf-8") as file:
            file.write(rows)

    def make_file(self, filename: str, template: str, /, *args, **kwargs):
        self._make_file(filename, self._render(template, *args, **kwargs))