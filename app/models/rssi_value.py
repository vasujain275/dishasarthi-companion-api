from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class RSSIValue(Base):
    __tablename__ = "rssi_values"

    sample_id = Column(Integer, ForeignKey("samples.id"), primary_key=True)
    bssid = Column(String, primary_key=True)
    rssi = Column(Integer)

    sample = relationship("Sample", back_populates="rssi_values")
