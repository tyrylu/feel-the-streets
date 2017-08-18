from sqlalchemy import Column, ForeignKey, Boolean, Enum, Float, Integer
from . import Road
from .enums import Amenity

class ServiceRoad(Road):
    __tablename__ = "service_roads"
    __mapper_args__ = {'polymorphic_identity': 'service_road'}
    id = Column(Integer, ForeignKey("roads.id"), primary_key=True)
    emergency = Column(Boolean)
    delivery = Column(Boolean)
    amenity = Column(Enum(Amenity))
    maxwidth = Column(Float)
    bus = Column(Boolean)