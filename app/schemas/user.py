from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None


class UserResponse(UserBase):
    id: int
    places: List["PlaceResponse"] = []

    model_config = ConfigDict(from_attributes=True)


from app.schemas.place import PlaceResponse
