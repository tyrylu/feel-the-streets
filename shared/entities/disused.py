import enum
from . import Named
from .enums import Amenity, RoadType

class DisusedType(enum.Enum):
    quarry = 0
    yes = 1

class Disused(Named):
    type: DisusedType
    denomination: str = None
    destroyed_amenity: Amenity = None
    destroyed_name: str = None
    end_date: str = None
    start_date: str = None
    wikipedia: str = None
    religion: str = None
    highway: RoadType = None
    operator: str = None
    foot: bool = None
    layer: int = None
    wikidata: str = None
    note: str = None