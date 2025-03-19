from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List


class RSSISample(BaseModel):
    timestamp: datetime
    rssi_values: Dict[str, int]  # BSSID: RSSI value


class CollectData(BaseModel):
    username: str
    location: str
    place: str
    samples: List[RSSISample]
