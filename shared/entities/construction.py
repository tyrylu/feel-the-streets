import enum
from . import Named
from .enums import ConstructionType, RoadType

class Construction(Named):
    type: ConstructionType
    official_name: str = None
    wikidata: str = None
    wikipedia: str = None
    bridge: bool = None
    layer: int = None
    abandoned_highway: RoadType = None
    abandoned_ref: str = None
    official_en_name: str = None
    note: str = None
    official_name_1: str = None
