import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer
from ..sa_types import IntEnum
from . import Leisure
from .enums import OSMObjectType

class GardenType(enum.Enum):
    residential = 0
    botanical = 1
    monastery = 2
    castle = 3
    arboretum = 4
    

class Garden(Leisure):
    __tablename__ = "gardens"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["leisures.id", "leisures.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'garden'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    garden_type = Column(IntEnum(GardenType))