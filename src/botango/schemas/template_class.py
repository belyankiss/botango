from jinja2 import Template
from pydantic import BaseModel, ConfigDict

class ManagerTemplate(BaseModel):
    filename: str
    template: Template

    model_config = ConfigDict(arbitrary_types_allowed=True)