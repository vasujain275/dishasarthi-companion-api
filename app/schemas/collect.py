from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Dict, List


class RSSISample(BaseModel):
    timestamp: datetime
    rssi_values: Dict[str, int]  # BSSID: RSSI value

    @field_validator("timestamp", mode="before")
    @classmethod
    def convert_to_naive(cls, v):
        # If the datetime is timezone-aware, convert to naive UTC
        if isinstance(v, datetime) and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class CollectData(BaseModel):
    username: str
    location: str
    place: str
    samples: List[RSSISample]
