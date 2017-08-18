import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, Enum, UnicodeText
from sqlalchemy.orm import relationship
from .enums import Amenity, TourismType, AerialWayType, RailWayType, ManMade, AccessType
from .entity import Entity

class AreaType(enum.Enum):
    unclassified = 0
    pedestrian = 1
    platform = 2
    service = 3
    yes = 4
    path = 5

class Area(Entity):
    __tablename__ = "areas"
    __mapper_args__ = {'polymorphic_identity': 'area'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(Enum(AreaType), nullable=False)
    name = Column(UnicodeText)
    amenity = Column(Enum(Amenity))
    layer = Column(Integer)
    surface = Column(UnicodeText)
    bicycle = Column(Boolean)
    foot = Column(Boolean)
    lit = Column(Boolean)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    tourism = Column(Enum(TourismType))
    aeroway = Column(Enum(AerialWayType))
    railway = Column(Enum(RailWayType))
    man_made = Column(Enum(ManMade))
    floating = Column(Boolean)
    access = Column(Enum(AccessType))