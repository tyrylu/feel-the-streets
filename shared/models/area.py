import enum
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from .enums import Amenity, TourismType, AerialWayType, RailWayType, ManMade, AccessType, OSMObjectType
from .entity import Entity

class AreaType(enum.Enum):
    unclassified = 0
    pedestrian = 1
    platform = 2
    service = 3
    yes = 4
    path = 5
    footway = 6
    rest_area = 7
    living_street = 8
    residential = 9
    track = 10
    construction = 11
    elevator = 12
    
class Area(Entity):
    __tablename__ = "areas"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'area'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(AreaType), nullable=False)
    name = Column(UnicodeText)
    amenity = Column(IntEnum(Amenity))
    layer = Column(Integer)
    surface = Column(UnicodeText)
    bicycle = Column(Boolean)
    foot = Column(Boolean)
    lit = Column(Boolean)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    tourism = Column(IntEnum(TourismType))
    aeroway = Column(IntEnum(AerialWayType))
    railway = Column(IntEnum(RailWayType))
    man_made = Column(IntEnum(ManMade))
    floating = Column(Boolean)
    access = Column(IntEnum(AccessType))