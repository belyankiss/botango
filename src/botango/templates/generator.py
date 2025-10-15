from pathlib import Path
from typing import Optional, Dict, Any


class GeneratorFiles:
    def __init__(
            self,
            filename: str,
            path: Optional[Path] = None,
            text: Optional[str] = None,
            data: Optional[Dict[str, Any]] = None
    ):
        self.path = path if path else Path(filename)
        self.text = text
        self.data = data

    def create_file(self, sep: Optional[str] = "="):
        if self.text:
            self.path.write_text(self.text)
        _data = []
        if self.data:
            for k, v in self.data.items():
                _data.append(f"{k}{sep}{v}")
        text = "\n".join(_data)
        self.path.write_text(text)
