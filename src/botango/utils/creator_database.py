from pathlib import Path
from typing import Union, ClassVar

from botango.databases import AioSQLiteDatabase, PostgresDatabase
from botango.templates._base_db import BaseTemplate
from botango.templates._connection import ConnectionTemplate
from botango.templates._create_database import CreateDatabase
from botango.templates._init_database import InitDatabase
from botango.templates._init_models import InitModels
from botango.templates._model_user import UserModel
from botango.utils.render_templates import render_template


class CreatorDatabase:


    dir_name: ClassVar[str] = "database"
    init_file: ClassVar[str] = "__init__.py"
    models_dir: ClassVar[str] = "models"
    connection_file: ClassVar[str] = "connection.py"
    base_file: ClassVar[str] = "base.py"
    create_database_file: ClassVar[str] = "create_database.py"
    user_model_file: ClassVar[str] = "user.py"


    def __init__(
            self,
            database: Union[AioSQLiteDatabase, PostgresDatabase]
    ):
        self.database = database
        self.db_path = Path(self.dir_name)
        self.db_path.mkdir(parents=True)

    def _create_connection(self):
        render_template(ConnectionTemplate(filename=(self.db_path / self.connection_file)), self.database.to_dict())

    def _make_models_dir(self):
        (self.db_path / self.models_dir).mkdir(parents=True)

    def _make_init_database(self):
        render_template(InitDatabase(filename=(self.db_path / "__init__.py")))

    def _make_init_models(self):
        render_template(InitModels(filename=(self.db_path / self.models_dir / self.init_file)))

    def _make_base_file(self):
        render_template(BaseTemplate(filename=(self.db_path / self.models_dir / self.base_file)))

    def _make_temp_user_model(self):
        render_template(UserModel(filename=(self.db_path / self.models_dir / self.user_model_file)))

    def _make_create_database_file(self):
        render_template(CreateDatabase(filename=(self.db_path / self.create_database_file)))

    def create_files(self):
        self._create_connection()
        self._make_models_dir()
        self._make_init_database()
        self._make_init_models()
        self._make_base_file()
        self._make_temp_user_model()
        self._make_create_database_file()

