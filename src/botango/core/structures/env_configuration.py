import os
from enum import StrEnum
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Any, Optional, Tuple, ClassVar

from pydantic import BaseModel

DATA_PATH = Path("data")
ENV_PATH = DATA_PATH / ".env"

class Comment(StrEnum):
    bot = "# Aiogram bot data"
    aiosqlite = "# Aiosqlite database data"
    postgresql = "# Postgresql database data"
    webhook = "# Webhook data"
    redis = "# Redis data"


class BaseEnv(BaseModel):
    name: Optional[str] = None
    comment: Comment = None

class BotEnv(BaseEnv):
    name: str = "bot"
    comment: Comment = Comment.bot
    BOT_TOKEN: str = "Your bot token"

class BaseEnvAiosqlite(BaseEnv):
    name: str = "aiosqlite"
    comment: Comment = Comment.aiosqlite
    DB_NAME: str = "example_database.db"

class BaseEnvPostgresql(BaseEnv):
    name: str = "postgresql"
    comment: Comment = Comment.postgresql
    POSTGRES_NAME: str =  "example_database"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

class WebhookEnv(BaseEnv):
    name: str = "webhook"
    comment: Comment = Comment.webhook
    WEBHOOK_URL: str = "https://your-domain.com"
    WEBHOOK_PATH: str = "/webhook"
    WEBHOOK_SECRET: str = "very-secret-value"

class RedisEnv(BaseEnv):
    name: str = "redis"
    comment: Comment = Comment.redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379


class EnvCreator:
    path: ClassVar[Path] = ENV_PATH
    exclude_values: ClassVar[Tuple[str, ...]] = ("name", "comment")

    @classmethod
    def load(cls):
        """
        Загрузка файла .env и создание при его отсутствии.
        :return:
        """
        if not cls.path.exists():
            cls._create()
        d: Dict[str, str] = {}
        with cls.path.open("r", encoding="utf-8") as f:
            for row in f:
                row = row.strip()
                if not row or row.startswith("#") or "=" not in row:
                    continue
                k, v = row.split("=", 1)
                d[k.strip()] = v.strip()
        return d

    @classmethod
    def _create(cls):
        data = cls._default_env()
        DATA_PATH.mkdir(parents=True, exist_ok=True)
        with cls.path.open("w", encoding="utf-8") as f:
            for k, v in data.items():
                f.write(f"{k}={v}\n")

    @classmethod
    def _default_env(cls) -> Dict[str, str]:
        c = BotEnv()
        return c.model_dump(exclude={"name"})

    @classmethod
    def _rewrite_env_file(cls, data: Dict[str, Any]):
        DATA_PATH.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", delete=False, dir=DATA_PATH, encoding="utf-8") as tf:
            for k, v in data.items():
                if k not in cls.exclude_values:
                    tf.write(f"{k}={v}\n")
            tmp = tf.name
        os.replace(tmp, cls.path)

    @classmethod
    def add(cls, model: BaseEnv):
        data = cls.load()
        for k, v in model.model_dump().items():
            if k not in data and k not in cls.exclude_values:
                data[k] = v
        cls._rewrite_env_file(data)

    @classmethod
    def delete(cls, model: BaseEnv):
        data = cls.load()
        [data.pop(v, None) for v in model.model_dump().keys()]
        cls._rewrite_env_file(data)
