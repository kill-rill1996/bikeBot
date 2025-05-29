from typing import List

from pydantic import BaseModel


class Category(BaseModel):
    id: int
    title: str
    emoji: str | None = None


class TransportNumber(BaseModel):
    id: int
    subcategory_title: str
    serial_number: int


class JobTitle(BaseModel):
    id: int
    title: str


class Subcategory(BaseModel):
    id: int
    title: str
    category_id: int


class CategoryJobtypes(Category):
    jobtypes: List["Jobtype"]


class Jobtype(BaseModel):
    id: int
    title: str
    emoji: str | None = None


class JobtypeCategories(Jobtype):
    transport_categories: List[Category]


class Job(BaseModel):
    id: int
    title: str
    jobtype_id: int

