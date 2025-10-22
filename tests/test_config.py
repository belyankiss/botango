# test_config.py
from botango.core.project_config import config


def test_config():
    # Тестируем выбор компонентов
    selected = ["docker", "base", "handlers"]
    errors = config.validate_component_selection(selected)

    if errors:
        print("Ошибки конфигурации:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Конфигурация валидна!")

        # Получаем зависимости
        all_deps = []
        for comp_name in selected:
            component = config.get_component_by_name(comp_name)
            if component:
                all_deps.extend(component.get_requirement_strings())

        print("Зависимости:", list(set(all_deps)))


if __name__ == "__main__":
    test_config()