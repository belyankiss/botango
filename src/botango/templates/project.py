import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import List, Optional

from botango.templates._gitignore import GITIGNORE


class CreateProject:
    def __init__(self, bot_name: str):
        self._path = Path(bot_name)
        self._bot_name = bot_name

        if self._path.exists():
            print(f"❌ Папка '{bot_name}' уже существует.")
            sys.exit(1)

    def make_project(self, db: str = None, token: str = None, redis: bool = False, docker: bool = False, payments: List[str] = None):
        (self._path).mkdir(parents=True)
        (self._path / ".env").write_text(
            f"""BOT_TOKEN={token}"""
        )
        (self._path / "settings.py").write_text(
            """from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()"""
        )
        (self._path / "main.py").write_text(
            """import asyncio

from botango import LongPollingBot
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from settings import settings

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

app = LongPollingBot(
    bot=bot
)

if __name__ == '__main__':
    asyncio.run(app.run())"""
        )
        (self._path / ".gitignore").write_text(GITIGNORE)
        print(f"✅ Бот '{self._bot_name}' успешно создан!")
        print(f"➡ Перейди в каталог: cd {self._bot_name}")
        print(f"➡ Запусти: python app/main.py")

class Databases(StrEnum):
    aiosqlite = "aiosqlite"
    postgresql = "postgresql"

    @classmethod
    def default(cls):
        return cls.aiosqlite.value

class Payments(StrEnum):
    cryptobot = "cryptobot"
    xrocket = "xrocket"
    yoomoney = "yoomoney"

class ProjectGenerator:
    def __init__(
            self,
            dir_name: str,
            token: str,
            db: Optional[Databases] = None,
            name_db: Optional[str] = "database",
            redis: bool = False,
            docker: bool = False,
            payments: List[Payments] = None
    ):
        self.dir_name = dir_name
        self.token = token
        self.db = db
        self.name_db = name_db
        self.redis = redis
        self.docker = docker
        self.payments = payments
        self.path = Path(self.dir_name)
        if self.path.exists():
            print(f"❌ Папка '{dir_name}' уже существует.")
            sys.exit(1)
        self._env_data = {}

    def _add_env(self):
        ...


