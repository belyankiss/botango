from dataclasses import dataclass


@dataclass(frozen=True)
class Commands:
    newbot: str = "newbot"
    add: str = "add"
    help: str = "help"