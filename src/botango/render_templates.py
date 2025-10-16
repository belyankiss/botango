from typing import Dict, Any

from botango.schemas.template_class import ManagerTemplate


def render_template(template: ManagerTemplate, data: Dict[str, Any] = None):
    with open(file=template.filename, mode="w", encoding="utf-8") as file:
        if data:
            file.write(template.template.render(**data))
        else:
            file.write(template.template.render())