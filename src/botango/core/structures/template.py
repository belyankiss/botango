from pathlib import Path
from typing import Optional, Union, Dict, Any

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field

TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "templates"

class Rendering:
    @classmethod
    def _env(cls) -> Environment:
        return Environment(
            loader=FileSystemLoader(TEMPLATE_PATH),
            trim_blocks=True,
            lstrip_blocks=True
        )

    @classmethod
    def _render(
            cls,
            template_file: Optional[Union[str, Path]] = None,
            data: Optional[Dict[str, Any]] = None
    ) -> str:
        env = cls._env()
        tpl = env.get_template(name=template_file)
        return tpl.render(**(data or {}))

    @classmethod
    def make(
            cls,
            target_file: Path,
            template_file: Optional[Union[str, Path]] = None,
            data: Optional[Dict[str, Any]] = None
    ):
        rows = cls._render(template_file, data)
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(rows, encoding="utf-8")


class Template(BaseModel):
    target_file: Union[str, Path]
    template_file: Optional[Union[str, Path]] = None
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @classmethod
    def path(
            cls,
            base_path: Path,
            target_file: str,
            template_file: Optional[str] = None,
            data: Optional[Dict[str, Any]] = None
    ) -> "Template":

        return cls(
            target_file=(base_path / target_file),
            template_file=template_file,
            data=data
        )

    @classmethod
    def render(
            cls,
            base_path: Path,
            target_file: str,
            template_file: Optional[str] = None,
            data: Optional[Dict[str, Any]] = None
    ):
        file = cls.path(base_path, target_file, template_file, data)
        Rendering.make(target_file=file.target_file, template_file=file.template_file, data=file.data)
