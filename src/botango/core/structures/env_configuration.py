import os
from enum import StrEnum
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Any, Optional, Tuple, ClassVar

from pydantic import BaseModel

DATA_PATH = Path("data")
ENV_PATH = DATA_PATH / ".env"

class NamesEnv(StrEnum):
    bot = "bot"
    aiosqlite = "aiosqlite"
    postgres = "postgres"
    webhook = "webhook"
    redis = "redis"
    cryptobot = "cryptobot"

class DefaultFieldEnv(StrEnum):
    bot = "Your-bot-token"
    db_name_aiosqlite = "example_database.db"
    postgres_name = "example_database"
    postgres_user = "postgres"
    postgres_password = "postgres"
    postgres_host = "localhost"
    postgres_port = "5432"
    webhook_url = "https://your-domain.com"
    webhook_path = "/webhook"
    webhook_secret = "very-secret-value"
    redis_host = "localhost"
    redis_port = "6379"
    cryptobot_token = "Your cryptobot token here!"

class BaseEnv(BaseModel):
    name: Optional[str] = None

class BotEnv(BaseEnv):
    name: NamesEnv = NamesEnv.bot
    BOT_TOKEN: DefaultFieldEnv = DefaultFieldEnv.bot

class AiosqliteEnv(BaseEnv):
    name: NamesEnv = NamesEnv.aiosqlite
    DB_NAME: DefaultFieldEnv = DefaultFieldEnv.db_name_aiosqlite

class PostgresEnv(BaseEnv):
    name: NamesEnv = NamesEnv.postgres
    POSTGRES_NAME: DefaultFieldEnv =  DefaultFieldEnv.postgres_name
    POSTGRES_USER: DefaultFieldEnv = DefaultFieldEnv.postgres_user
    POSTGRES_PASSWORD: DefaultFieldEnv = DefaultFieldEnv.postgres_password
    POSTGRES_HOST: DefaultFieldEnv = DefaultFieldEnv.postgres_host
    POSTGRES_PORT: DefaultFieldEnv = DefaultFieldEnv.postgres_port

class WebhookEnv(BaseEnv):
    name: NamesEnv = NamesEnv.webhook
    WEBHOOK_URL: DefaultFieldEnv = DefaultFieldEnv.webhook_url
    WEBHOOK_PATH: DefaultFieldEnv = DefaultFieldEnv.webhook_path
    WEBHOOK_SECRET: DefaultFieldEnv = DefaultFieldEnv.webhook_secret

class RedisEnv(BaseEnv):
    name: NamesEnv = NamesEnv.redis
    REDIS_HOST: DefaultFieldEnv = DefaultFieldEnv.redis_host
    REDIS_PORT: DefaultFieldEnv = DefaultFieldEnv.redis_port

class CryptoBotEnv(BaseEnv):
    name: NamesEnv = NamesEnv.cryptobot
    CRYPTOBOT_TOKEN: DefaultFieldEnv = DefaultFieldEnv.cryptobot_token


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
                if k not in cls.exclude_values:
                    f.write(f"{k}={v}\n")

    @classmethod
    def _default_env(cls) -> Dict[str, Any]:
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
        if isinstance(model, AiosqliteEnv):
            [data.pop(v, None) for v in PostgresEnv().model_dump(exclude={"name"}).keys()]
        if isinstance(model, PostgresEnv):
            [data.pop(v, None) for v in AiosqliteEnv().model_dump(exclude={"name"}).keys()]
        for k, v in model.model_dump().items():
            if k not in data and k not in cls.exclude_values:
                data[k] = v
        cls._rewrite_env_file(data)

    @classmethod
    def delete(cls, model: BaseEnv):
        data = cls.load()
        [data.pop(v, None) for v in model.model_dump().keys()]
        cls._rewrite_env_file(data)

if __name__ == '__main__':
    b = EnvCreator()
    b.add(AiosqliteEnv())
    b.add(PostgresEnv())
    b.add(CryptoBotEnv())