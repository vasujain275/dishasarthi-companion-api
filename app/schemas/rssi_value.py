from pydantic import BaseModel, ConfigDict
from typing import Optional


class RSSIValueBase(BaseModel):
    bssid: str
    rssi: int


class RSSIValueCreate(RSSIValueBase):
    pass


class RSSIValueUpdate(BaseModel):
    rssi: Optional[int] = None


class RSSIValueResponse(RSSIValueBase):
    sample_id: int

    model_config = ConfigDict(from_attributes=True)
