from pathlib import Path

from jinja2 import Template

from botango.schemas.template_class import ManagerTemplate
from .enviroment_jinja import ENV

MODEL_USER_TEMPLATE = ENV.from_string(
    """'''Example database model User'''

from sqlalchemy import Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class UserDbModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    """
)

class UserModel(ManagerTemplate):
    filename: Path
    template: Template = MODEL_USER_TEMPLATE