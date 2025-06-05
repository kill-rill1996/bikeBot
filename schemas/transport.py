from pydantic import BaseModel


class Transport(BaseModel):
    id: int
    category_id: int
    subcategory_id: int
    serial_number: int


class TransportSubcategory(BaseModel):
    id: int
    category_id: int
    subcategory_id: int
    serial_number: int
    subcategory_title: str

