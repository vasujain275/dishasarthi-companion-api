from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .rssi_value import RSSIValueResponse
from .rssi_value import RSSIValueCreate


class SampleBase(BaseModel):
    location_id: int


class SampleCreate(BaseModel):
    location_id: int
    timestamp: datetime  # Add this field
    rssi_values: List[RSSIValueCreate] = []


class SampleUpdate(BaseModel):
    location_id: Optional[int] = None


class SampleResponse(SampleBase):
    id: int
    timestamp: datetime
    rssi_values: List[RSSIValueResponse] = []

    class Config:
        orm_mode = True
