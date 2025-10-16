import sys
from pathlib import Path

from botango.utils.package_loader import PackageLoader
from botango.utils.render_templates import RenderTemplate
from botango.schemas.project_schema import ProjectSchema

DEFAULT_FILES = {
    "main.py": "main.j2",
    "settings.py": "settings.j2",
    ".gitignore": "gitignore.j2",
    ".env": "env.j2"
}

DATABASE_FILES = {
    "database/__init__.py": "database/init.j2",
    "database/connection.py": "database/connection.j2",
    "database/models/__init__.py": "database/models/init.j2",
    "database/models/base.py": "database/models/base.j2",
    "database/models/user.py": "database/models/user.j2"
}




class CreatorProject:
    def __init__(
            self,
            project_schema: ProjectSchema
    ):
        self.project_schema = project_schema
        self.project_path = Path(project_schema.name)
        self.project_path.mkdir(parents=True, exist_ok=True)
        self.render_template = RenderTemplate()

    def _create_default_files(self):
        for k, v in DEFAULT_FILES.items():
            self.render_template.make_file(k, v, **self.project_schema.model_dump())

    def _create_database_files(self):
        for k, v in DATABASE_FILES.items():
            self.render_template.make_file(k, v, **self.project_schema.database.to_dict())

    def _install_db_dependencies(self):
        if self.project_schema.database:
            PackageLoader(self.project_schema.database.__dependencies__, self.project_schema.database.__version__)
            self._install_sqlalchemy()

    @staticmethod
    def _install_sqlalchemy():
        PackageLoader("sqlalchemy", version="2.0.44")


    def create(self):
        self._create_default_files()
        if self.project_schema.database:
            Path("database/models").mkdir(parents=True, exist_ok=True)
            self._create_database_files()
            self._install_db_dependencies()
            self._install_sqlalchemy()