import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, ClassVar

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, TemplateSyntaxError
from pydantic import BaseModel, Field, ConfigDict

# Путь до папки с шаблонами (берётся на два уровня выше текущего файла)
TemplateDirectory: Path = Path(__file__).resolve().parents[2] / "templates"

# Настраиваем логгер для отслеживания ошибок шаблонов
logger = logging.getLogger(__name__)


class Template(BaseModel):
    """
    Класс для генерации файлов на основе Jinja2 шаблонов.

    Каждый экземпляр Template отвечает за создание одного файла
    по одному шаблону с переданными данными.
    """

    base_directory: Path                # Папка, в которой создаётся файл
    target_file: Path                   # Путь до результирующего файла
    template_file: Path                 # Путь до шаблона .j2
    data: Dict[str, Any] = Field(default_factory=dict)  # Данные для подстановки в шаблон

    # Конфигурация Jinja2 — общий объект среды для всех шаблонов
    environment: ClassVar[Environment] = Environment(
        loader=FileSystemLoader(TemplateDirectory),
        trim_blocks=True,
        lstrip_blocks=True
    )

    # Разрешаем использование произвольных типов (например Path)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(
        __pydantic_self__,
        *,
        base_directory: str,
        target_file: str,
        data: Dict[str, Any] = None,
        **_pydantic_kwargs: Any
    ):
        """
        Конструктор инициализирует пути и данные.
        """
        p = Path(base_directory)
        super().__init__(
            base_directory=p,
            target_file=p / target_file,
            template_file=p / f"{target_file}.j2",
            data=data or {},
            **_pydantic_kwargs
        )

    def _render(self) -> str:
        """
        Отрисовывает шаблон Jinja2 с переданными данными.
        Возвращает итоговый текст для записи в файл.
        """
        try:
            tpl = self.environment.get_template(name=str(self.template_file))
            return tpl.render(**self.data)
        except TemplateNotFound:
            logger.exception("Template not found: %s", self.template_file)
            raise
        except TemplateSyntaxError:
            logger.exception("Syntax error in template: %s", self.template_file)
            raise

    def _write_atomic(self, content: str):
        """
        Безопасная запись файла через временный файл (atomic write).

        1. Создаётся временный файл.
        2. В него записывается содержимое.
        3. Временный файл заменяет целевой — без риска частичной записи.
        """
        self.target_file.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=str(self.target_file.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, str(self.target_file))
        finally:
            # На случай, если произошла ошибка до замены
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def create(self):
        """
        Основной метод: отрисовывает шаблон и создаёт файл.
        """
        rows = self._render()
        self._write_atomic(rows)