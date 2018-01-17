import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Amenity
from .enums import OSMObjectType, SurveillanceType, SurveillanceKind, SurveillanceZone

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
    __mapper_args__ = {'polymorphic_identity': 'bicycle_parking', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("amenities.id"), primary_key=True)
    parking_type = Column(IntEnum(BicycleParkingType))
    surveillance = Column(IntEnum(SurveillanceType))
    surveillance_type = Column(IntEnum(SurveillanceKind))
    surveillance_zone = Column(IntEnum(SurveillanceZone))
    food = Column(Boolean)
    real_ale = Column(Boolean)
    service_chain_tool = Column(Boolean)
