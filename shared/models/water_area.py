import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

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
    
    

class WaterArea(Named):
    __tablename__ = "water_areas"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'water_area'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(WaterAreaType))
    reservoir_type = Column(UnicodeText)
    alt_name = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    alt_name = Column(UnicodeText)
    