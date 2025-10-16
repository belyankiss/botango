import sys
from pathlib import Path

from botango.utils.creator_database import CreatorDatabase
from botango.utils.package_loader import PackageLoader
from botango.utils.render_templates import render_template
from botango.schemas.project_schema import ProjectSchema
from botango.templates._env import EnvTemplate
from botango.templates._gitignore import GitIgnoreTemplate
from botango.templates._main import MainTemplate
from botango.templates._settings import SettingsTemplate


class CreatorProject:
    def __init__(
            self,
            project_schema: ProjectSchema
    ):
        self.project_schema = project_schema
        self.project_path = Path(project_schema.name)
        if self.project_path.exists():
            print(f"Проект с таким названием уже существует: {project_schema.name}")
            sys.exit(1)

    def _create_env(self):
        render_template(EnvTemplate(), self.project_schema.model_dump())

    @staticmethod
    def _create_gitignore():
        render_template(GitIgnoreTemplate())

    def _create_main(self):
        render_template(MainTemplate(), self.project_schema.model_dump())

    def _create_settings(self):
        render_template(SettingsTemplate(), self.project_schema.model_dump())

    def _install_db_dependencies(self):
        if self.project_schema.database:
            PackageLoader(self.project_schema.database.__dependencies__, version="0.21.0")
            self._install_sqlalchemy()

    @staticmethod
    def _install_sqlalchemy():
        PackageLoader("sqlalchemy", version="2.0.44")


    def create(self):
        self.project_path.mkdir(parents=True)
        (self.project_path / "__init__.py").write_text("# create bot by botango")
        self._create_gitignore()
        self._create_settings()
        self._create_main()
        self._create_env()
        self._install_db_dependencies()
        if self.project_schema.database:
            creator_database = CreatorDatabase(database=self.project_schema.database)
            creator_database.create_files()