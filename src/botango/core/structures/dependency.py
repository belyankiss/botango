from enum import Enum
from typing import Optional

from pydantic import BaseModel


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
DJANGO = Dependency.exact(name="django", version="5.0.0")

AIOHTTP = Dependency.latest("aiohttp")
REQUESTS = Dependency.latest("requests")

DOCKER = Dependency(name="docker", version="7.1.0")
DOCKER_COMPOSE = Dependency(name="docker-compose", version="1.29.2")