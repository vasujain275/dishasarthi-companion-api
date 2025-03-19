from pydantic import BaseModel
from typing import List, Optional
from .sample import SampleResponse


class LocationBase(BaseModel):
    name: str
    place_id: int


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    place_id: Optional[int] = None


class LocationResponse(LocationBase):
    id: int
    samples: List[SampleResponse] = []

    class Config:
        orm_mode = True
