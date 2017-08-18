import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from .enums import LeisureType, Amenity, ManMade, SmokingType, TourismType, SportType, InfoType, HistoricType, RoofShape
from . import Addressable

class TakeAway(enum.Enum):
    no = 0
    yes = 1
    only = 2

class LocationType(enum.Enum):
    none = 0
    underground = 1
class IndustrialType(enum.Enum):
    none = 0
    factory = 1
    distributor = 2

class Building(Addressable):
    __tablename__ = "buildings"
    __mapper_args__ = {'polymorphic_identity': 'building'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    levels = Column(Integer)
    flats = Column(Integer)
    opening_hours = Column(UnicodeText)
    amenity = Column(Enum(Amenity))
    religion = Column(UnicodeText)
    official_name = Column(UnicodeText)
    capacity = Column(Integer)
    start_date = Column(UnicodeText)
    denomination = Column(UnicodeText)
    layer = Column(Integer)
    takeaway = Column(Enum(TakeAway))
    smoking = Column(Enum(SmokingType))
    delivery = Column(Boolean)
    emergency = Column(Boolean)
    leisure_type = Column(Enum(LeisureType))
    tourism_type = Column(Enum(TourismType))
    man_made = Column(Enum(ManMade))
    operator = Column(UnicodeText)
    industrial_type = Column(Enum(IndustrialType))
    roof_height = Column(Integer)
    roof_shape = Column(Enum(RoofShape))
    height = Column(Integer)
    internet_access_fee = Column(Boolean)
    wikidata = Column(UnicodeText)
    internet_access = Column(UnicodeText)
    sport = Column(Enum(SportType))
    covered = Column(Boolean)
    alt_name = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    old_name = Column(UnicodeText)
    short_name = Column(UnicodeText)
    information_type = Column(Enum(InfoType))
    description = Column(UnicodeText)
    location = Column(Enum(LocationType))
    product = Column(UnicodeText)
    dispensing = Column(Boolean)
    colour = Column(UnicodeText)
    community_centre_for = Column(UnicodeText)
    historic_type = Column(Enum(HistoricType))
    cuisine = Column(UnicodeText)
    phone = Column(UnicodeText)
    email = Column(UnicodeText)
    outdoor_seating = Column(Boolean)
    brewery = Column(UnicodeText)
    vegetarian_diet = Column(Boolean)