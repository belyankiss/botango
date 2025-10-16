from typing import Union, Optional, Dict

from botango.databases.absrtact_db import AbstractDatabase


class PostgresDatabase(AbstractDatabase):
    name = "postgresql"
    __dependencies__ = "asyncpg"

    def __init__(
            self,
            host: str = "localhost",
            port: Union[str, int] = 5432,
            user: str = "postgres",
            password: str = "postgres",
            name_db: Optional[str] = None
    ):
        if name_db:
            self.name_db = name_db
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self._path = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{self.name_db}"

    def __repr__(self):
        var = []
        for k, v in self.__dict__.items():
            if not k.startswith("_") and not callable(v):
                if k == "password":
                    var.append(f"{k}={"*" * len(v)}")
                else:
                    var.append(f"{k}={v}")
        return (f"{self.__class__.__name__}("
                f"{", ".join(var)}"
                f")")
