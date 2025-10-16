from pathlib import Path

from jinja2 import Template

from botango.schemas.template_class import ManagerTemplate
from .enviroment_jinja import ENV

CREATE_DATABASE_TEMPLATE = ENV.from_string(
    """from .connection import engine
from .models import Base


async def create_database(delete_tables: bool = False):
    async with engine.begin() as conn:
        if delete_tables:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    """
)

class CreateDatabase(ManagerTemplate):
    filename: Path
    template: Template = CREATE_DATABASE_TEMPLATE