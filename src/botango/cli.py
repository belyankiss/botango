from pathlib import Path

import click

from .cli_commands import Commands


@click.group()
def cli():
    pass

@cli.command()
@click.argument("action", default="create")
def newbot(action):
    """Команда для работы с ботами"""
    if action == "help":
        print("Справка по команде newbot:")
        print("newbot - создает бота")
        print("newbot help - показывает справку")
    elif action == "create":
        path = Path()
        print("Создание нового бота...")
    else:
        print(f"Неизвестное действие: {action}")


@cli.command()
def help():
    click.echo(
        f"{click.style("Usage:", bold=True, fg="green")} "
        f"{click.style("botango", bold=True, fg="cyan")} "
        f"{click.style("[OPTIONS] <COMMAND>", fg="cyan")}\n\n"
        f"{click.style("Commands:", bold=True)}\n"
        f"  {click.style(f"{Commands.newbot}", fg="cyan", bold=True)}    Create new bot\n"
        f"  {click.style(f"{Commands.add}", fg="cyan", bold=True)}       Add essence to project\n"
        f"  {click.style(f"{Commands.help}", fg="cyan", bold=True)}      Display documentation for a command"
    )