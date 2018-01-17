import enum
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from .enums import Amenity, TourismType, AerialWayType, RailWayType, ManMade, AccessType, OSMObjectType, LeisureType, SportType, BarrierType, AreaType, AttractionType, LandType, HistoricType
from .entity import Entity

class Area(Entity):
    __tablename__ = "areas"
    __mapper_args__ = {'polymorphic_identity': 'area', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
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
    sorting_name = Column(UnicodeText)
    landuse = Column(IntEnum(LandType))
    historic = Column(IntEnum(HistoricType))
    url = Column(UnicodeText)
    email = Column(UnicodeText)
