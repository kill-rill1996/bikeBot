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


class OperationShow(BaseModel):
    id: int
    serial_number: int
    transport_category: str
    transport_subcategory: str
    created_at: datetime.datetime
    job_title: str


class OperationDetails(BaseModel):
    id: int
    created_at: datetime.datetime
    comment: str
    duration: int
    serial_number: int
    transport_category: str
    transport_subcategory: str
    job_title: str

