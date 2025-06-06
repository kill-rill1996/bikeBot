from typing import List

from pydantic import BaseModel


class Category(BaseModel):
    id: int
    title: str
    emoji: str | None = None


class CategoryId(BaseModel):
    id: int


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

