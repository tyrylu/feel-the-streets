from . import ManMade
from .enums import BuildingPartType, BuildingType, TourismType, RoofShape, TowerType

class Tower(ManMade):
    tower_type: TowerType = None
    building_part: BuildingPartType = None
    building: BuildingType = None
    tourism: TourismType = None
    fee: bool = None
    mobile_phone_communication: bool = None
    tower_construction: str = None
    colour: str = None
    roof_shape: RoofShape = None
    levels: int = None
    alt_name: str = None
    min_height: int = None
    roof_colour: str = None
    phone: str = None
    ele: int = None
    opening_hours: str = None
    flats: int = None
    microwave_communication: bool = None
    television_communication: bool = None
    communication: str = None