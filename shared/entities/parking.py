import enum
from .enums import AccessType, BuildingType, WheelchairAccess, BarrierType, ParkingType, ConstructionType, LandType, GardenType
from . import Named, Address

class Smoothness(enum.Enum):
    excellent = 0
    intermediate = 1
    good = 2

class Parking(Named):
    paid: str = None
    capacity: int = None
    capacity_for_disabled: str = None
     # Someone treats it as a bool, someone as an int.
    operator: str = None
    access: AccessType = None
    type: ParkingType = None
    supervised: bool = None
    designation: str = None
    building_type: BuildingType = None
    surface: str = None
    address: Address = None
    park_ride: bool = None
    layer: int = None
    website: str = None
    building_levels: int = None
    opening_hours: str = None
    start_date: str = None
    wheelchair: WheelchairAccess = None
    barrier: BarrierType = None
    capacity_for_parents: bool = None
    capacity_for_women: bool = None
    lit: bool = None
    description: str = None
    fixme: str = None
    covered: bool = None
    construction: ConstructionType = None
    landuse: LandType = None
    maxstay: str = None
    maxheight: float = None
    smoothness: Smoothness = None
    fenced: bool = None
    level: str = None
    email: str = None
    bus: bool = None
    garden_type: GardenType = None
    foot: bool = None
    height: str = None
    demolished_building: BuildingType = None
    bicycle: bool = None
    motorcycle: bool = None
    old_name: str = None