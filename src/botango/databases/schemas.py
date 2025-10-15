from typing import Union, Optional

from pydantic import BaseModel, ConfigDict

from botango.databases import AioSQLiteDatabase, PostgresDatabase


class WebHookData(BaseModel):
    host: str
    port: Union[int, str]
    url_path: str

class ModeSchema(BaseModel):
    type: str
    data: Optional[WebHookData] = None


class ProjectSchema(BaseModel):
    name: str
    token: str
    mode: ModeSchema
    database: Union[AioSQLiteDatabase, PostgresDatabase, None] = None
    redis: bool
    docker: bool

    model_config = ConfigDict(arbitrary_types_allowed=True)