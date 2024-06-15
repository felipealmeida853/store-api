from datetime import datetime
from pydantic import BaseModel


class FileBaseSchema(BaseModel):
    name: str
    user_uuid: str
    key: str | None = None
    created_at: datetime | None = None
    bucket: str | None = None