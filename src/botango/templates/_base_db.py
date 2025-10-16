from pathlib import Path

from jinja2 import Template

from botango.schemas.template_class import ManagerTemplate
from .enviroment_jinja import ENV

BASE_TEMPLATE = ENV.from_string("""from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
""")

class BaseTemplate(ManagerTemplate):
    filename: Path
    template: Template = BASE_TEMPLATE