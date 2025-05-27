from typing import List

from pydantic import BaseModel
import datetime


class OperationAdd(BaseModel):
    tg_id: str
    transport_id: int
    duration: int
    location_id: int
    comment: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    jobs_ids: List[int] | None = None


class Operation(OperationAdd):
    id: int


class OperationJob(BaseModel):
    id: int
    serial_number: int
    transport_category: str
    transport_subcategory: str
    created_at: datetime.datetime
    job_title: str


class OperationJobs(BaseModel):
    id: int
    serial_number: int
    transport_category: str
    transport_subcategory: str
    created_at: datetime.datetime
    jobs_titles: list[str] = None


class OperationDetailJobs(BaseModel):
    id: int
    created_at: datetime.datetime
    comment: str
    duration: int
    serial_number: int
    transport_category: str
    transport_subcategory: str
    jobs_titles: list[str] | None = None


