from __future__ import annotations

import asyncio
from typing import List, Dict, Any, Union, Optional

import click
from aiogram import Bot
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.utils.token import TokenValidationError

from botango.databases.absrtact_db import AbstractDatabase
from botango.databases.aiosqlite_db import AioSQLiteDatabase
from botango.databases.postgres_db import PostgresDatabase
from botango.databases.schemas import ProjectSchema

def validate_https_host(host: str) -> str:
    if not host.startswith("https://"):
        raise click.BadParameter("Хост должен начинаться с 'https://'")
    return host

def validate_token(ctx, param, token: str) -> str:
    try:
        Bot(token)
    except TokenValidationError:
        raise click.BadParameter(f"Некорректный формат токена. Ожидается 123456789:AAxxx...")
    return token


def num_list(
    list_var: List[str],
    echo_message: str,
    settings_message: str,
    default_value: Optional[int] = None,
) -> Optional[str]:
    """
    Показывает нумерованный список и возвращает выбранный элемент (строку),
    либо None, если пользователь нажал Enter (пропустить).
    """
    if not list_var:
        return None

    click.echo(echo_message)
    for i, m in enumerate(list_var, 1):
        click.echo(f"{i}. {m}")

    prompt_text = "Введите номер (или Enter чтобы пропустить)"
    # показываем default только если он не None
    if default_value is not None:
        prompt_text += f" [{default_value}]"

    while True:
        # читаем как строку — пустая строка означает пропустить
        raw = click.prompt(prompt_text, default="" if default_value is None else str(default_value), show_default=False)
        raw = str(raw).strip()
        if raw == "":
            click.echo(f"{settings_message}: пропущено")
            return None
        if not raw.isdigit():
            click.echo("Некорректный ввод — введите номер пункта или Enter для пропуска.")
            continue
        idx = int(raw)
        if idx < 1 or idx > len(list_var):
            click.echo("Некорректный номер. Попробуйте ещё раз.")
            continue
        choice = list_var[idx - 1]
        click.echo(f"{settings_message}: {choice}")
        return choice

def choice_setting_bot(data: Dict[str, Any]):
    mode_bot = ["webhook", "long_polling"]
    mode = num_list(
        list_var=mode_bot,
        echo_message="Выберите режим работы бота:",
        settings_message="Режим работы бота",
        default_value=2
    )
    if mode == "webhook":
        host = click.prompt("Введите хост для webhook", default=None, value_proc=validate_https_host)
        port = click.prompt("Введите порт для webhook", default=8000, type=int)
        url_path = click.prompt("Введите путь для webhook", default="/webhook")
        data["mode"] = {"type": "webhook", "data": {"host": host, "port": port, "url_path": url_path}}
    else:
        data["mode"] = {"type": "long_polling"}

def choice_database(data: Dict[str, Any]):
    cls_database = None
    db_choice = num_list(
        list_var=AbstractDatabase.list_databases(),
        echo_message="Выберите базу данных:",
        settings_message="База данных",
        default_value=None
    )
    if db_choice == "postgresql":
        host = click.prompt("Введите url для PostgreSQL:", default="localhost")
        port = click.prompt("Введите порт для PostgreSQL:", default=5432, type=int)
        user = click.prompt("Введите имя пользователя PostgreSQL:", default="postgres")
        password = click.prompt("Введите пароль пользователя PostgreSQL:", default="postgres")
        name_db = click.prompt("Введите название базы данных PostgreSQL:", default="botango_database")
        cls_database = PostgresDatabase(host, port, user, password, name_db)
    elif db_choice == "aiosqlite":
        name_db = click.prompt("Введите название базы данных AioSQLite:", default="botango_database")
        cls_database = AioSQLiteDatabase(name_db)

    data["database"] = cls_database


@click.group()
def cli():
    pass

@cli.command()
@click.argument("name")
@click.option("--token", prompt="Введите токен бота, который получили в @BotFather", hide_input=True, callback=validate_token)
def newbot(name, token):
    async def check_token():
        bot = Bot(token)
        async with bot:
            try:
                me = await bot.get_me()
                click.echo(f"✅ Токен действителен. Это бот @{me.username}")
            except TelegramUnauthorizedError:
                raise click.ClickException("❌ Токен недействителен. Telegram вернул ошибку авторизации.")
            finally:
                await bot.session.close()
    asyncio.run(check_token())
    data = {
        "name": name,
        "token": token,
    }
    choice_setting_bot(data)

    choice_database(data)

    add_redis = click.confirm("Добавить Redis?", default=False)

    data["redis"] = add_redis

    add_docker = click.confirm("Сделать файлы Docker и docker-compose.yaml?", default=False)

    data["docker"] = add_docker

    print(ProjectSchema(**data))












