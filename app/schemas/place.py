from pydantic import BaseModel, ConfigDict
from typing import List, Optional


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
    locations: List["LocationResponse"] = []

    model_config = ConfigDict(from_attributes=True)


from app.schemas.location import LocationResponse
