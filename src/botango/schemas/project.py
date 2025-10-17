from typing import Optional

from pydantic import BaseModel

from botango.schemas.database import DatabaseData
from botango.schemas.mode import ModeSchema


class Project(BaseModel):
    name: str
    token: str
    mode: ModeSchema = ModeSchema()
    database: Optional[DatabaseData] = None
    redis: bool = False
    docker: bool = False