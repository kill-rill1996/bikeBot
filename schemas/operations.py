from pydantic import BaseModel
import datetime


class OperationAdd(BaseModel):
    tg_id: str
    transport_id: int
    job_id: int
    duration: int
    location_id: int
    comment: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


class Operation(OperationAdd):
    id: int