import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer
from ..sa_types import IntEnum
from . import Amenity
from .enums import OSMObjectType

class BicycleParkingType(enum.Enum):
    unknown = 0
    stands = 1
    lockers = 2
    ground_slots = 3
    wall_loops = 4
    informal = 5
    anchors = 6
    shed = 7
    wall_hoops = 8
    rack = 9
    

class BicycleParking(Amenity):
    __tablename__ = "bicycle_parkings"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["amenities.id", "amenities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'bicycle_parking'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    parking_type = Column(IntEnum(BicycleParkingType))
    lit = Column(Boolean)