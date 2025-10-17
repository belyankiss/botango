import uuid
from typing import Union

from pydantic import BaseModel, Field


class WebHookData(BaseModel):
    host: str = Field(..., description="Для использования webhook адрес должен начинаться с https://")
    port: Union[int, str] = 8000
    url_path: str = '/webhook'
    webhook_secret: str = str(uuid.uuid4())