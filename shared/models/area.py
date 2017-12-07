import enum
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from .enums import Amenity, TourismType, AerialWayType, RailWayType, ManMade, AccessType, OSMObjectType, LeisureType, SportType, BarrierType, AreaType
from .entity import Entity

class AttractionType(enum.Enum):
    animal = 0

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
    old_name = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    leisure = Column(IntEnum(LeisureType))
    sport = Column(IntEnum(SportType))
    note = Column(UnicodeText)
    alt_name = Column(UnicodeText)
    website = Column(UnicodeText)
    barrier = Column(IntEnum(BarrierType))
    animal = Column(UnicodeText)
    attraction = Column(IntEnum(AttractionType))