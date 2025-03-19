from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Sample(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    location_id = Column(Integer, ForeignKey("locations.id"))

    location = relationship("Location", back_populates="samples")
    rssi_values = relationship("RSSIValue", back_populates="sample")
