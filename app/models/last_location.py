from sqlalchemy import Column, Float, Integer, UnicodeText
from . import Base

class LastLocation(Base):
    __tablename__ = "last_locations"
    id = Column(Integer, primary_key=True)
    area = Column(UnicodeText, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)