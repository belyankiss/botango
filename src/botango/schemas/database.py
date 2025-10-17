from typing import ClassVar, List, Optional, Union

from pydantic import BaseModel, field_validator


class BaseDatabase(BaseModel):
    name: str
    name_database: str
    dependency: str
    version: str
    __name_databases__: ClassVar[List[str]] = []

    @classmethod
    def get_name(cls):
        return cls.name

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.name not in cls.__name_databases__:
            cls.__name_databases__.append(cls.name)

class AioSQLiteData(BaseDatabase):
    name: str = "aiosqlite"
    name_database: str = "botango.db"
    dependency: str = "aiosqlite"
    version: str = "0.21.0"

    @field_validator("name_database", mode="before")
    def validate_name_db(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) >= 2:
            return f"{parts[0]}.db"
        return f"{v}.db"

class PostgresData(AioSQLiteData):
    name: str = "postgresql"
    name_database: str = "botango"
    host: str
    port: int
    user: str
    password: str
    dependency: str = "asyncpg"
    version: str = "0.30.0"

    def __repr__(self):
        masked = "*" * len(self.password)
        return (
            f"PostgresData("
            f"name_database='{self.name_database}', "
            f"host='{self.host}', port={self.port}, "
            f"user='{self.user}', password={masked!r})"
        )

    __str__ = __repr__

    @field_validator("name_database", mode="before")
    def validate_name_db(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) == 1:
            return v
        return parts[0]

class DatabaseData(BaseModel):
    name: Optional[str] = None
    data: Optional[Union[AioSQLiteData, PostgresData]] = None
    dependency: Optional[str] = None
    version: Optional[str] = None