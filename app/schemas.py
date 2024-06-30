from datetime import datetime

from pydantic import BaseModel


class FileBaseSchema(BaseModel):
    name: str
    user: str
    folder_uuid: str
    key: str | None = None
    created_at: datetime | None = None
    bucket: str | None = None


class FolderBaseSchema(BaseModel):
    name: str
    user: str
    folder_uuid: str
    created_at: datetime | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    password: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    verified: bool | None = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
