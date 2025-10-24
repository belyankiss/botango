import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, List

import toml

logger = logging.getLogger(__name__)


# Тип, который мы храним: mapping class_name -> {"class": [values...]}
TomlData = Dict[str, Dict[str, List[str]]]


class TomlCreator:
    """
    Утилита для чтения/записи простых toml-файлов со структурой:
    {
        "ModelName": {"class": ["val1", "val2"]},
        ...
    }
    """

    encoding = "utf-8"

    def __init__(self, name_file: str):
        self.path = Path(name_file)

    def write(self, data: TomlData) -> None:
        """Атомарно записать данные в toml-файл (перезаписывает полностью)."""
        # ensure parent dir exists
        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)

        # atomic write via mkstemp + replace
        fd, tmp_path = tempfile.mkstemp(dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "w", encoding=self.encoding) as f:
                toml.dump(data, f)
            os.replace(tmp_path, str(self.path))
            logger.debug("Файл %s создан/обновлен", self.path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def read(self) -> TomlData:
        """Прочитать toml-файл. Если файла нет — вернуть пустой dict."""
        if not self.path.exists():
            logger.debug("Файл %s не найден — возвращаю пустой словарь", self.path)
            return {}
        try:
            with self.path.open("r", encoding=self.encoding) as f:
                data = toml.load(f)
            # Нормализуем структуру — гарантируем нужную форму
            normalized: TomlData = {}
            for k, v in data.items():
                if isinstance(v, dict):
                    vals = v.get("class", [])
                    if isinstance(vals, list):
                        normalized[k] = {"class": [str(x) for x in vals]}
                    else:
                        # если "class" не список — приводим к списку
                        normalized[k] = {"class": [str(vals)]}
                else:
                    # если запись некорректного формата — приводим в ожидаемую форму
                    normalized[k] = {"class": [str(v)]}
            logger.debug("Файл %s прочитан", self.path)
            return normalized
        except Exception:
            logger.exception("Ошибка при чтении %s", self.path)
            raise

    def rewrite(self, data: TomlData, *, prefer_new: bool = True) -> None:
        """
        Объединить существующие данные и новые и записать в файл.
        По умолчанию prefer_new=True — новые значения перезаписывают существующие.
        Если prefer_new=False — существующие значения будут иметь приоритет (existing wins).
        """
        existing = self.read()
        merged: TomlData = {}

        # start from existing, then update with data or vice versa depending on prefer_new
        base = existing if not prefer_new else {}
        overlay = data if prefer_new else {}

        # merge base first
        for k, v in existing.items():
            merged[k] = {"class": list(v.get("class", []))}

        # apply overlay (new data)
        for k, v in data.items():
            # ensure proper shape
            vals = v.get("class") if isinstance(v, dict) else None
            if vals is None:
                vals = []
            # replace or create
            merged[k] = {"class": list(vals)}

        self.write(merged)

    def add_model(self, name: str) -> None:
        """Добавить новую модель (секцию) с пустым списком 'class'."""
        data = self.read()
        if name in data:
            logger.info("Модель %s уже существует", name)
            return
        data[name] = {"class": []}
        self.write(data)
        logger.info("Модель %s успешно добавлена", name)

    def add_value(self, class_name: str, value: str) -> None:
        """
        Добавить значение в список class для секции class_name.
        Если секции нет — создаём её.
        """
        data = self.read()
        section = data.setdefault(class_name, {"class": []})
        values = section.get("class")
        if not isinstance(values, list):
            values = []
            section["class"] = values

        if value in values:
            logger.info("Значение %s уже присутствует в модели %s", value, class_name)
            return

        values.append(value)
        self.write(data)
        logger.info("Значение %s добавлено в модель %s", value, class_name)

    def delete_class(self, class_name: str) -> None:
        data = self.read()
        if class_name in data:
            del data[class_name]
            self.write(data)
            logger.info("Модель %s успешно удалена", class_name)
        else:
            logger.info("Модель %s не найдена", class_name)

    def delete_value(self, class_name: str, value: str) -> None:
        data = self.read()
        section = data.get(class_name)
        if not section:
            logger.info("Модель %s не найдена", class_name)
            return
        values = section.get("class", [])
        if value in values:
            values.remove(value)
            # если список стал пуст — можно оставить секцию или удалить её — здесь оставим пустую
            section["class"] = values
            self.write(data)
            logger.info("Значение %s удалено из модели %s", value, class_name)
        else:
            logger.info("Значение %s не найдено в модели %s", value, class_name)
