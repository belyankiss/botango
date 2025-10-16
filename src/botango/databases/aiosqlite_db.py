from typing import Optional, Dict, Type, Self, overload

from botango.databases.absrtact_db import AbstractDatabase


class AioSQLiteDatabase(AbstractDatabase):
    name = "aiosqlite"
    name_db = "db"
    __dependencies__ = "aiosqlite"
    __version__ = "0.21.0"

    def __init__(self, name_db: Optional[str]):
        if name_db:
            if "." in name_db:
                name_db = name_db.split(".")[0]
            self.name_db = f"{name_db}.db"

