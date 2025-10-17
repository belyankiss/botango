from __future__ import annotations

from typing import List, Dict, Any, Optional

import click
from aiogram import Bot
from aiogram.utils.token import TokenValidationError

from botango.schemas import Project
from botango.schemas import (
    AioSQLiteData,
    BaseDatabase,
    DatabaseData,
    ModeSchema,
    PostgresData,
    WebHookData
)
from botango.utils.cli_funcs import check_token
from botango.utils.creator_project import CreatorProject


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

def choice_setting_bot(project_schema: Project):
    mode = num_list(
        list_var=project_schema.mode.allowed_methods(),
        echo_message="Выберите режим работы бота:",
        settings_message="Режим работы бота",
        default_value=2
    )
    mode_schema = ModeSchema(type=mode)
    project_schema.mode = mode_schema
    if mode == "webhook":
        host = click.prompt("Введите хост для webhook", default=None, value_proc=validate_https_host)
        webhook_data = WebHookData(host=host)
        port = click.prompt("Введите порт для webhook", default=8000, type=int)
        webhook_data.port = port
        url_path = click.prompt("Введите путь для webhook", default="/webhook")
        webhook_data.url_path = url_path
        mode_schema.data = webhook_data

def choice_database(project_schema: Project):
    database_data = None
    db_choice = num_list(
        list_var=BaseDatabase.__name_databases__,
        echo_message="Выберите базу данных:",
        settings_message="База данных",
        default_value=None
    )
    data = None
    if db_choice == "postgresql":
        host = click.prompt("Введите url для PostgreSQL:", default="localhost")
        port = click.prompt("Введите порт для PostgreSQL:", default=5432, type=int)
        user = click.prompt("Введите имя пользователя PostgreSQL:", default="postgres")
        password = click.prompt("Введите пароль пользователя PostgreSQL:", default="postgres")
        name_database = click.prompt("Введите название базы данных PostgreSQL:", default="botango")
        data = PostgresData(
            name_database=name_database,
            host=host,
            port=port,
            user=user,
            password=password
        )
    elif db_choice == "aiosqlite":
        name_database = click.prompt("Введите название базы данных AioSQLite:", default="botango.db")
        data = AioSQLiteData(name_database=name_database)
    if data:
        database_data = DatabaseData(
            name=db_choice,
            data=data
        )
    project_schema.database = database_data

def add_docker(data: Dict[str, Any]):
    docker_mode = ["github_secret", "environment"]
    choice = click.confirm("Сделать файлы Docker и docker-compose.yaml?", default=False)

    if choice:
        docker_choice = num_list(
            docker_mode,
            echo_message="Где вы будете хранить чувствительные данные?",
            settings_message="Место хранения",
            default_value=2
        )


@click.group()
def cli():
    pass

@cli.command()
@click.argument("name")
@click.option("--token", prompt="Введите токен бота, который получили в @BotFather", hide_input=True, callback=validate_token)
def newbot(name, token):
    check_token(token)
    project_schema = Project(
        name=name,
        token=token
    )
    choice_setting_bot(project_schema)

    choice_database(project_schema)

    add_redis = click.confirm("Добавить Redis?", default=False)

    project_schema.redis = add_redis
    creator_project = CreatorProject(project_schema)
    creator_project.create()












