from pydantic import BaseModel, ConfigDict
from typing import List, Optional


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
    samples: List["SampleResponse"] = []

    model_config = ConfigDict(from_attributes=True)


from app.schemas.sample import SampleResponse
