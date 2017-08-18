import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from . import Named

class WaterAreaType(enum.Enum):
    unknown = 0
    pond = 1
    reservoir = 2
    river = 3

class WaterArea(Named):
    __tablename__ = "water_areas"
    __mapper_args__ = {'polymorphic_identity': 'water_area'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(WaterAreaType))
    reservoir_type = Column(UnicodeText)