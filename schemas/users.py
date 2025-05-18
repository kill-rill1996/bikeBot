import datetime
from typing import List

from pydantic import BaseModel


class AllowUser(BaseModel):
    id: int
    tg_id: str
