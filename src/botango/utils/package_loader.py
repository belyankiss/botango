import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Optional


class PackageLoader:
    def __init__(
            self,
            package_name: str,
            version: Optional[str] = None
    ):
        self.package_name = package_name
        self.version = version
        self._install_package()

    def _search_package(self) -> bool:
        return bool(importlib.util.find_spec(self.package_name))

    @staticmethod
    def _create_requirements():
        file = Path("requirements.txt")
        if file.exists():
            file.unlink()

        with file.open("w", encoding="utf-8") as f:
            subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                stdout=f,
                check=True,
            )

        print("requirements.txt создан!")

    def _install_package(self):
        if not self._search_package():
            if self.version:
                self.package_name = f"{self.package_name}=={self.version}"
            print(f"Идет установка {self.package_name} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", self.package_name])
            self._create_requirements()

