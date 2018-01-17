import enum
from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, LandType, LandCover, SportType

class WaterAreaType(enum.Enum):
    unknown = 0
    pond = 1
    reservoir = 2
    river = 3
    wastewater = 4
    lock = 5
    reflecting_pool = 6
    lake = 7
    basin = 8
    intermittent = 9
    lagoon = 10
    water = 11
    oxbow = 12

class WaterArea(Named):
    __tablename__ = "water_areas"
    __mapper_args__ = {'polymorphic_identity': 'water_area', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(WaterAreaType))
    reservoir_type = Column(UnicodeText)
    alt_name = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    alt_name = Column(UnicodeText)
    landuse = Column(IntEnum(LandType))
    loc_name = Column(UnicodeText)
    note = Column(UnicodeText)
    landcover = Column(IntEnum(LandCover))
    website = Column(UnicodeText)
    sport = Column(IntEnum(SportType))

