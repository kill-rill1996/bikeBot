import datetime

from pydantic import BaseModel


class AllowUser(BaseModel):
    id: int
    tg_id: str


class User(BaseModel):
    id: int
    tg_id: str
    tg_username: str
    username: str
    created_at: datetime.datetime
    role: str
    lang: str  # en, ru, es



