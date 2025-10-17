from typing import Optional

from pydantic import BaseModel

from botango.schemas.webhook import WebHookData


class ModeSchema(BaseModel):
    type: str = "long_polling"
    data: Optional[WebHookData] = None

    @staticmethod
    def allowed_methods():
        return ["webhook", "long_polling"]
