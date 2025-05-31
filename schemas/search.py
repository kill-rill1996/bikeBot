import datetime

from pydantic import BaseModel


class TransportNumber(BaseModel):
    id: int
    subcategory_title: str
    serial_number: int


class JobTitle(BaseModel):
    id: int
    title: str


class OperationJobTransport(BaseModel):
    id: int
    transport_id: int
    serial_number: int
    transport_subcategory: str
    job_id: int
    job_title: str


class OperationJobUserLocation(BaseModel):
    id: int
    created_at: datetime.datetime
    category_title: str
    subcategory_title: str
    serial_number: int
    job_title: str
    job_type: str
    duration: int
    location: str
    username: str
    role: str
    comment: str


class OperationJobsUserLocation(BaseModel):
    id: int
    created_at: datetime.datetime
    category_title: str
    subcategory_title: str
    serial_number: int
    jobs: list[tuple[str, str]]  # jop_title, job_type
    duration: int
    location: str
    username: str
    role: str
    comment: str


class ListOperations(BaseModel):
    operations: list[OperationJobsUserLocation]

