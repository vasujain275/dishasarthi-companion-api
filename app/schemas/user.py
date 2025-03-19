from pydantic import BaseModel
from typing import List, Optional
from .place import PlaceResponse


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None


class UserResponse(UserBase):
    id: int
    places: List[PlaceResponse] = []

    class Config:
        orm_mode = True
