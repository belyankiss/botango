import abc
from typing import ClassVar, Dict, Any, List, Type


class AbstractDatabase(abc.ABC):
    name: ClassVar[str]
    name_db: str = "database"
    _path: str
    _data: Dict[str, str] = None
    _registry: ClassVar[Dict[str, Type["AbstractDatabase"]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "name"):
            raise TypeError(f"{cls.__name__} must define class variable 'name'")
        if cls.name not in cls._registry:
            cls._registry[cls.name] = cls

    @classmethod
    def databases(cls) -> Dict[str, Any]:
        return dict(cls._registry)

    @classmethod
    def list_databases(cls) -> List[Any]:
        return list(cls.databases().keys())

    def __repr__(self):
        var = []
        for k, v in self.__dict__.items():
            if not k.startswith("_") and not callable(v):
                var.append(f"{k}={v}")
        return (f"{self.__class__.__name__}("
                f"{", ".join(var)}"
                f")")






