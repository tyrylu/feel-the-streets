import enum
from . import Named
from .enums import LandType, LandCover, SportType

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
    type: WaterAreaType = None
    reservoir_type: str = None
    alt_name: str = None
    wikidata: str = None
    wikipedia: str = None
    alt_name: str = None
    landuse: LandType = None
    loc_name: str = None
    note: str = None
    landcover: LandCover = None
    website: str = None
    sport: SportType = None
