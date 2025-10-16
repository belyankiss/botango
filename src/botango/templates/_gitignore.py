from jinja2 import Template

from botango.schemas.template_class import ManagerTemplate
from .enviroment_jinja import ENV

GITIGNORE = ENV.from_string(
""".gitignore
__pycache__/
*.pyc
.env
.venv/
venv/
.dist-info/
build/
dist/
.DS_Store
*.db
*.sqlite3
*.iml
*.xml
.idea
""")

class GitIgnoreTemplate(ManagerTemplate):
    filename: str = ".gitignore"
    template: Template = GITIGNORE