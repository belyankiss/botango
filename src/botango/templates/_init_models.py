from pathlib import Path

from jinja2 import Template

from botango.schemas.template_class import ManagerTemplate
from .enviroment_jinja import ENV

INIT_MODELS = ENV.from_string("""from .base import Base
from .user import UserDbModel
""")

class InitModels(ManagerTemplate):
    filename: Path
    template: Template = INIT_MODELS