from pydantic import BaseModel
from typing import List, Optional
from .location import LocationResponse


class PlaceBase(BaseModel):
    name: str
    user_id: int


class PlaceCreate(PlaceBase):
    pass


class PlaceUpdate(BaseModel):
    name: Optional[str] = None
    user_id: Optional[int] = None


class PlaceResponse(PlaceBase):
    id: int
    locations: List[LocationResponse] = []

    class Config:
        orm_mode = True
