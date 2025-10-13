import sys
from pathlib import Path


class CreateProject:
    def __init__(self, bot_name: str):
        self._path = Path(bot_name)
        self._bot_name = bot_name

        if self._path.exists():
            print(f"❌ Папка '{bot_name}' уже существует.")
            sys.exit(1)

    def make_project(self):
        (self._path / "app").mkdir(parents=True)
        (self._path / "app" / "__init__.py").touch()
        (self._path / "app" / ".env").write_text(
            """BOT_TOKEN="""
        )
        (self._path / "app" / "settings.py").write_text(
            """from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()"""
        )
        (self._path / "app" / "main.py").write_text(
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
        print(f"✅ Бот '{self._bot_name}' успешно создан!")
        print(f"➡ Перейди в каталог: cd {self._bot_name}")
        print(f"➡ Запусти: python app/main.py")
