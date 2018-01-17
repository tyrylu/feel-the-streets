import enum
from sqlalchemy import Column, ForeignKey, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Road
from .enums import Amenity, OSMObjectType, AccessType, ParkingType

class ServiceRoad(Road):
    __tablename__ = "service_roads"
    __mapper_args__ = {'polymorphic_identity': 'service_road', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("roads.id"), primary_key=True)
    delivery = Column(Boolean)
    frequency = Column(Integer)
    vehicle_backward = Column(IntEnum(AccessType))
    parking = Column(IntEnum(ParkingType))
    todo = Column(UnicodeText)
