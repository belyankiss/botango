import importlib.util
import os
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

        self._install_package(version)

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

    def _install_package(self, version: Optional[str] = None):
        if not self._search_package():
            if version:
                p = f"{self.package_name}=={version}"
            else:
                p = self.package_name
            print(f"Идет установка {self.package_name} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", p])
            self._create_requirements()

