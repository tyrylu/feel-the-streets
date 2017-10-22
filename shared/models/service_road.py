from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Float, Integer
from ..sa_types import IntEnum
from . import Road
from .enums import Amenity, OSMObjectType

class ServiceRoad(Road):
    __tablename__ = "service_roads"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["roads.id", "roads.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'service_road'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    emergency = Column(Boolean)
    delivery = Column(Boolean)
    amenity = Column(IntEnum(Amenity))
    maxwidth = Column(Float)
    bus = Column(Boolean)