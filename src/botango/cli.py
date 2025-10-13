import sys

from botango.templates.project import CreateProject



def main():
    if len(sys.argv) < 2:
        print("Использование: botango newbot <имя_бота>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "newbot":
        if len(sys.argv) < 3:
            print("Укажи имя бота: botango newbot mybot")
            sys.exit(1)
        bot_name = sys.argv[2]
        project = CreateProject(bot_name)
        project.make_project()
    else:
        print(f"Неизвестная команда: {command}")
        print("Доступные команды: newbot")
