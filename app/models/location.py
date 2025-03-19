from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    place_id = Column(Integer, ForeignKey("places.id"))

    place = relationship("Place", back_populates="locations")
    samples = relationship("Sample", back_populates="location")
