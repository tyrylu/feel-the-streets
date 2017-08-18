import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from . import Amenity

class DisplayType(enum.Enum):
    none = 0
    sundial = 1

class SupportType(enum.Enum):
    none = 0
    wall_mounted = 1
    ground = 2

class Clock(Amenity):
    __tablename__ = "clocks"
    __mapper_args__ = {'polymorphic_identity': 'clock'}
    id = Column(Integer, ForeignKey("amenities.id"), primary_key=True)
    display = Column(Enum(DisplayType))
    support = Column(Enum(SupportType))
    faces = Column(Integer)