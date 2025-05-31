from typing import List

from pydantic import BaseModel


class TransportCategory(BaseModel):
    title: str
    emoji: str | None = None
