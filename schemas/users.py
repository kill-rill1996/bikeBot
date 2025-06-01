import datetime

from pydantic import BaseModel


class AllowUser(BaseModel):
    id: int
    tg_id: str


class User(BaseModel):
    id: int
    tg_id: str
    tg_username: str | None = None
    username: str
    created_at: datetime.datetime
    role: str
    is_active: bool
    lang: str  # en, ru, es



