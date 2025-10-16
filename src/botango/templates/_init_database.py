from pathlib import Path

from jinja2 import Template

from botango.schemas.template_class import ManagerTemplate
from .enviroment_jinja import ENV

INIT_DATABASE = ENV.from_string('''from .connection import AsyncSessionLocal, get_session, close_engine, run_in_transaction

__all__ = [
    "AsyncSessionLocal",
    "close_engine",
    "get_session",
    "run_in_transaction"
]
''')

class InitDatabase(ManagerTemplate):
    filename: Path
    template: Template = INIT_DATABASE