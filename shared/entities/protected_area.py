import enum
from . import Named
from .enums import LandType

class ProtectedAreaType(enum.Enum):
    unknown = 0
    nature_reserve = 1
    boundary = 2
    
class ProtectedArea(Named):
    protect_class: int = None
    type: ProtectedAreaType = None
    website: str = None
    start_date: str = None
    protection_title: str = None
    wikipedia: str = None
    wikidata: str = None
    alt_name: str = None
    landuse: LandType = None
    fireplace: bool = None
    description_cz: str = None