import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer
from ..sa_types import IntEnum
from . import Amenity
from .enums import OSMObjectType

class DisplayType(enum.Enum):
    none = 0
    sundial = 1
    analog = 2
    digital = 3
    unorthodox = 4

class SupportType(enum.Enum):
    none = 0
    wall_mounted = 1
    ground = 2
    pole = 3
    billboard = 4
    tower = 5
    wall = 6
    

class Clock(Amenity):
    __tablename__ = "clocks"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["amenities.id", "amenities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'clock'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    display = Column(IntEnum(DisplayType))
    support = Column(IntEnum(SupportType))
    faces = Column(Integer)