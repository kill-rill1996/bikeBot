from typing import List

from pydantic import BaseModel
import datetime

from schemas.categories_and_jobs import Jobtype
from schemas.transport import Transport


class OperationAdd(BaseModel):
    tg_id: str
    transport_id: int
    duration: int
    location_id: int
    comment: str | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    jobs_ids: List[int] | None = None


class Operation(OperationAdd):
    id: int


class OperationJob(BaseModel):
    id: int
    duration: int
    serial_number: int
    transport_category: str
    transport_subcategory: str
    created_at: datetime.datetime
    job_title: str


class OperationJobs(BaseModel):
    id: int
    duration: int
    serial_number: int
    transport_category: str
    transport_subcategory: str
    created_at: datetime.datetime
    jobs_titles: list[str] = None


class OperationDetailJobs(BaseModel):
    id: int
    created_at: datetime.datetime
    comment: str | None = None
    duration: int
    serial_number: int
    transport_category: str
    transport_subcategory: str
    jobs_titles: list[str] | None = None


class OperationJobTransport(BaseModel):
    id: int
    transport_id: int
    serial_number: int
    transport_subcategory: str
    job_id: int
    job_title: str


