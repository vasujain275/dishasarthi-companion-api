from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class SampleBase(BaseModel):
    location_id: int
    timestamp: datetime


class SampleCreate(SampleBase):
    rssi_values: List["RSSIValueCreate"] = []


class SampleUpdate(BaseModel):
    location_id: Optional[int] = None
    timestamp: Optional[datetime] = None


class SampleResponse(SampleBase):
    id: int
    rssi_values: List["RSSIValueResponse"] = []

    model_config = ConfigDict(from_attributes=True)


from app.schemas.rssi_value import RSSIValueCreate, RSSIValueResponse
