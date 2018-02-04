from . import Leisure
from .enums import GardenType, LandType

class Garden(Leisure):
    garden_type: GardenType = None
    landuse: LandType = None
    bicycle: bool = None
    smoking: bool = None
    official_name: str = None