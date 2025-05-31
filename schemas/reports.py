import datetime
from typing import List

from pydantic import BaseModel


class JobWithJobtypeTitle(BaseModel):
    id: int
    title: str
    jobtype_title: str


class OperationWithJobs(BaseModel):
    id: int
    tg_id: str
    transport_category: str
    transport_subcategory: str
    transport_serial_number: int
    duration: int
    location_id: int
    comment: str | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    jobs: List[JobWithJobtypeTitle] | None = None


class OperationWithJobsMech(OperationWithJobs):
    mechanic: str


class JobForJobtypes(BaseModel):
    job_title: str
    subcategory_title: str
    serial_number: int
