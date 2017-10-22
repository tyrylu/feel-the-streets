import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import LeisureType, Amenity, ManMade, SmokingType, TourismType, SportType, InfoType, HistoricType, RoofShape, Location, AccessType, OSMObjectType, IndustrialType
from . import Addressable

class TakeAway(enum.Enum):
    no = 0
    yes = 1
    only = 2


class EmergencyType(enum.Enum):
    no = 0
    yes = 1
    ambulance_station = 2

class Building(Addressable):
    __tablename__ = "buildings"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["addressables.id", "addressables.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'building'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    levels = Column(Integer)
    flats = Column(Integer)
    opening_hours = Column(UnicodeText)
    amenity = Column(IntEnum(Amenity))
    religion = Column(UnicodeText)
    official_name = Column(UnicodeText)
    capacity = Column(Integer)
    start_date = Column(UnicodeText)
    denomination = Column(UnicodeText)
    layer = Column(Integer)
    takeaway = Column(IntEnum(TakeAway))
    smoking = Column(IntEnum(SmokingType))
    delivery = Column(Boolean)
    emergency = Column(IntEnum(EmergencyType))
    leisure_type = Column(IntEnum(LeisureType))
    tourism_type = Column(IntEnum(TourismType))
    man_made = Column(IntEnum(ManMade))
    operator = Column(UnicodeText)
    industrial_type = Column(IntEnum(IndustrialType))
    roof_height = Column(Integer)
    roof_shape = Column(IntEnum(RoofShape))
    height = Column(Integer)
    internet_access_fee = Column(Boolean)
    wikidata = Column(UnicodeText)
    internet_access = Column(UnicodeText)
    sport = Column(IntEnum(SportType))
    covered = Column(Boolean)
    alt_name = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    old_name = Column(UnicodeText)
    short_name = Column(UnicodeText)
    information_type = Column(IntEnum(InfoType))
    description = Column(UnicodeText)
    location = Column(IntEnum(Location))
    product = Column(UnicodeText)
    dispensing = Column(Boolean)
    colour = Column(UnicodeText)
    community_centre_for = Column(UnicodeText)
    historic_type = Column(IntEnum(HistoricType))
    cuisine = Column(UnicodeText)
    phone = Column(UnicodeText)
    email = Column(UnicodeText)
    outdoor_seating = Column(Boolean)
    brewery = Column(UnicodeText)
    vegetarian_diet = Column(Boolean)
    heritage = Column(Integer)
    heritage_operator = Column(UnicodeText)
    access = Column(IntEnum(AccessType))