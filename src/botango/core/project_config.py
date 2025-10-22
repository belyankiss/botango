from enum import Enum
from typing import List, Optional, Union, overload

from pydantic import BaseModel, Field


class VersionSeparator(str, Enum):
    EXACT = "=="
    GREATER_EQUAL = ">="
    GREATER = ">"
    LESS_EQUAL = "<="
    LESS = "<"
    COMPATIBLE = "~="


class Dependency(BaseModel):
    name: str
    version: Optional[str] = None
    separator: VersionSeparator = VersionSeparator.GREATER_EQUAL
    optional: bool = False

    def pack(self) -> str:
        if self.version:
            return f"{self.name}{self.separator.value}{self.version}"
        return self.name

    @classmethod
    def exact(cls, name: str, version: str) -> "Dependency":
        return cls(name=name, version=version, separator=VersionSeparator.EXACT)

    @classmethod
    def latest(cls, name: str) -> "Dependency":
        return cls(name=name, version=None)


AIOGRAM = Dependency(name="aiogram", version="3.8.0")
PYTHON_DOTENV = Dependency.latest("python-dotenv")

AIOSQLITE = Dependency(name="aiosqlite", version="0.20.0")
ASYNCPG = Dependency(name="asyncpg", version="0.30.0")
PSYCOPG2 = Dependency.exact("psycopg2-binary", "2.9.11")
SQLALCHEMY = Dependency(name="sqlalchemy", version="2.0.44")
ALEMBIC = Dependency(name="alembic", version="1.12.0")

FASTAPI = Dependency(name="fastapi", version="0.109.0")
UVICORN = Dependency.latest("uvicorn")
DJANGO = Dependency(name="django", version="5.0.0")

AIOHTTP = Dependency.latest("aiohttp")
REQUESTS = Dependency.latest("requests")

DOCKER = Dependency(name="docker", version="7.1.0")
DOCKER_COMPOSE = Dependency(name="docker-compose", version="1.29.2")

class Component(BaseModel):
    name: str
    description: str
    required: bool = False
    templates: str
    dependencies: List[Dependency] = Field(default_factory=list)
    conflicts_with: List[str] = Field(default_factory=list)
    requires: List[str] = Field(default_factory=list)

    # Методы для работы с зависимостями
    def get_dependencies(self) -> List[Dependency]:
        return self.dependencies

    def get_requirement_strings(self) -> List[str]:
        return [dep.pack() for dep in self.dependencies]

    def validate_compatibility(self, selected_components: List[str]) -> bool:
        """Проверяет совместимость с другими выбранными компонентами"""
        for conflict in self.conflicts_with:
            if conflict in selected_components:
                return False
        for requirement in self.requires:
            if requirement not in selected_components:
                return False
        return True

class DatabaseComponent(Component):
    """Базовый класс для компонентов базы данных"""
    db_type: str
    async_support: bool = True

class AioSQLiteDatabase(DatabaseComponent):
    name: str = "aiosqlite"
    description: str = "База данных SQLite с асинхронной поддержкой"
    required: bool = False
    templates: str = "templates/database/aiosqlite"
    db_type: str = "sqlite"
    dependencies: List[Dependency] = [AIOSQLITE, SQLALCHEMY]

class PostgresDatabase(DatabaseComponent):
    name: str = "postgresql"
    description: str = "База данных PostgreSQL с асинхронной поддержкой"
    required: bool = False
    templates: str = "templates/database/postgresql"
    db_type: str = "postgresql"
    dependencies: List[Dependency] = [ASYNCPG, SQLALCHEMY]
    requires: List[str] = ["base"]

class SyncPostgresDatabase(DatabaseComponent):
    name: str = "postgresql-sync"
    description: str = "База данных PostgreSQL с синхронным драйвером"
    required: bool = False
    templates: str = "templates/database/postgresql_sync"
    db_type: str = "postgresql"
    async_support: bool = False
    dependencies: List[Dependency] = [PSYCOPG2, SQLALCHEMY]
    conflicts_with: List[str] = ["aiosqlite", "postgresql"]

class DockerComponent(Component):
    name: str = "docker"
    description: str = "Docker конфигурация для развертывания"
    required: bool = False
    templates: str = "templates/docker"
    dependencies: List[Dependency] = [DOCKER, DOCKER_COMPOSE]

class DockerDatabaseComponent(DatabaseComponent):
    """База данных с Docker-специфичной конфигурацией"""
    volume_path: str = ""

class AioSQLiteDockerDatabase(DockerDatabaseComponent):
    name: str = "aiosqlite-docker"
    description: str = "SQLite с Docker и томом для данных"
    required: bool = False
    templates: str = "templates/database/aiosqlite-docker"
    db_type: str = "sqlite"
    volume_path: str = "./data:/app/data"
    dependencies: List[Dependency] = [AIOSQLITE, SQLALCHEMY]
    conflicts_with: List[str] =["aiosqlite", "postgresql", "postgresql-sync"]

class AlembicMigrationsComponent(Component):
    name: str = "migrations"
    description: str = "Миграции базы данных с Alembic"
    required: bool = False
    templates: str = "templates/migrations"
    dependencies: List[Dependency] = [ALEMBIC]
    requires: List[str] = ["database"]

class EnvironmentConfigComponent(Component):
    name: str = "env-config"
    description: str = "Конфигурация через .env файл"
    required: bool = True  # Делаем обязательным
    templates: str = "templates/env"
    dependencies: List[Dependency] = [PYTHON_DOTENV]


class WebFrameworkComponent(Component):
    """Компонент веб-фреймворка для админки или вебхуков"""
    framework_type: str


class FastAPIComponent(WebFrameworkComponent):
    name: str = "fastapi"
    description: str = "FastAPI для вебхуков и админ-панели"
    required: bool = False
    templates: str = "templates/web/fastapi"
    framework_type: str = "fastapi"
    dependencies: List[Dependency] = [FASTAPI, UVICORN]
    requires: List[str] = ["base"]


class DjangoComponent(WebFrameworkComponent):
    name: str = "django"
    description: str = "Django для админ-панели"
    required: bool = False
    templates: str = "templates/web/django"
    framework_type: str = "django"
    dependencies: List[Dependency] = [DJANGO]
    requires: List[str] = ["base"]


class BotangoConfig(BaseModel):
    """Основная конфигурация фреймворка"""

    # Базовые компоненты
    base: Component = Component(
        name="base",
        description="Базовая структура бота",
        required=True,
        templates="templates/base",
        dependencies=[AIOGRAM, PYTHON_DOTENV]
    )

    handlers: Component = Component(
        name="handlers",
        description="Обработчики сообщений и команд",
        required=True,
        templates="templates/handlers",
        requires=["base"]
    )

    keyboards: Component = Component(
        name="keyboards",
        description="Инлайн и реплай клавиатуры",
        required=False,
        templates="templates/keyboards",
        requires=["base", "handlers"]
    )

    middlewares: Component = Component(
        name="middlewares",
        description="Промежуточное ПО (throttling, ACL)",
        required=False,
        templates="templates/middlewares",
        requires=["base"]
    )

    services: Component = Component(
        name="services",
        description="Интеграции с внешними API",
        required=False,
        templates="templates/services",
        dependencies=[AIOHTTP],
        requires=["base"]
    )

    # Компоненты базы данных (выбирается один)
    database_components: List[DatabaseComponent] = Field(
        default_factory=lambda: [
            AioSQLiteDatabase(),
            PostgresDatabase(),
            SyncPostgresDatabase()
        ]
    )

    # Веб-компоненты (можно комбинировать)
    web_components: List[WebFrameworkComponent] = Field(
        default_factory=lambda: [
            FastAPIComponent(),
            DjangoComponent()
        ]
    )

    # Дополнительные компоненты
    webhook: Component = Component(
        name="webhook",
        description="Поддержка вебхуков вместо polling",
        required=False,
        templates="templates/webhook",
        requires=["base"],
        conflicts_with=["polling"]  # если добавим polling компонент
    )

    admin_panel: Component = Component(
        name="admin",
        description="Админ панель для управления ботом",
        required=False,
        templates="templates/admin",
        requires=["base", "database"]  # требует базу данных
    )

    docker: DockerComponent = DockerComponent()

    docker_databases: List[DockerDatabaseComponent] = Field(
        default_factory=lambda: [
            AioSQLiteDockerDatabase(),
        ]
    )

    migrations: AlembicMigrationsComponent = AlembicMigrationsComponent()

    # Методы для работы с конфигурацией
    def get_all_components(self) -> List[Component]:
        """Возвращает все доступные компоненты"""
        all_components = [
            self.base,
            self.handlers,
            self.keyboards,
            self.middlewares,
            self.services,
            self.webhook,
            self.admin_panel,
            self.docker,
            self.migrations
        ]
        all_components.extend(self.database_components)
        all_components.extend(self.web_components)
        return all_components

    def get_component_by_name(self, name: str) -> Optional[Component]:
        """Находит компонент по имени"""
        for component in self.get_all_components():
            if component.name == name:
                return component
        return None

    def validate_component_selection(self, selected_names: List[str]) -> List[str]:
        """Проверяет валидность выбранных компонентов и возвращает ошибки"""
        errors = []
        selected_components = []

        # Собираем компоненты по именам
        for name in selected_names:
            component = self.get_component_by_name(name)
            if component:
                selected_components.append(component)
            else:
                errors.append(f"Компонент '{name}' не найден")

        # Проверяем требования и конфликты
        for component in selected_components:
            if not component.validate_compatibility(selected_names):
                errors.append(f"Компонент '{component.name}' несовместим с выбранной конфигурацией")

        # Проверяем обязательные компоненты
        required_components = [comp for comp in self.get_all_components() if comp.required]
        for req_comp in required_components:
            if req_comp.name not in selected_names:
                errors.append(f"Обязательный компонент '{req_comp.name}' не выбран")

        docker_errors = self.validate_docker_compatibility(selected_names)
        errors.extend(docker_errors)

        return errors

    def get_docker_database_component(self, base_db_name: str) -> Optional[DockerDatabaseComponent]:
        """Получает Docker-версию компонента базы данных"""
        docker_name = f"{base_db_name}-docker"
        for db_comp in self.docker_databases:
            if db_comp.name == docker_name:
                return db_comp
        return None


    def validate_docker_compatibility(self, selected_names: List[str]) -> List[str]:
        """Проверяет совместимость Docker с другими компонентами"""
        errors = []

        # Проверяем, что если выбран docker, то база данных тоже docker-версия
        docker_selected = "docker" in selected_names
        has_regular_db = any(
            name in selected_names
            for name in ["aiosqlite", "postgresql", "postgresql-sync"]
        )
        has_docker_db = any(
            name in selected_names
            for name in [db.name for db in self.docker_databases]
        )

        if docker_selected and has_regular_db and not has_docker_db:
            errors.append("При использовании Docker выберите Docker-версию базы данных")

        return errors

config = BotangoConfig()

if __name__ == '__main__':
    print(config.database_components)

