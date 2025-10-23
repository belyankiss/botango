from typing import List

from pydantic import BaseModel, Field

from .dependency import Dependency
from .structure import Structure
from .template import Template


class Component(BaseModel):
    name: str
    description: str
    required: bool = False
    structure: Structure
    dependencies: List[Dependency] = Field(default_factory=list)
    requires: List[str] = Field(default_factory=list)

    # Методы для работы с зависимостями
    def get_dependencies(self) -> List[Dependency]:
        return self.dependencies

    def get_requirement_strings(self) -> List[str]:
        return [dep.pack() for dep in self.dependencies]


AioSQLiteComponent = Component(
    name="aiosqlite",
    description="Подключение базы данных",
    structure=Structure(
        templates=[
            Template(
                target_file="database/__init__.py",
                template_file="database/__init__.py.j2"
            )
        ]
    )
)