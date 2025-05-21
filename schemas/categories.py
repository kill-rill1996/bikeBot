from typing import List

from pydantic import BaseModel


class Category(BaseModel):
    id: int
    title: str
    emoji: str | None = None


class CategoryJobtypes(Category):
    jobtypes: List["Jobtype"]


class Jobtype(BaseModel):
    id: int
    title: str
    emoji: str | None = None


class JobtypeCategories(Jobtype):
    transport_categories: List[Category]


class Subcategory(BaseModel):
    id: int
    title: str
    category_id: int

