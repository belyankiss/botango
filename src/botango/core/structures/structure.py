from typing import List

from pydantic import BaseModel, Field

from .template import Template


class Structure(BaseModel):
    templates: List[Template] = Field(default_factory=list)