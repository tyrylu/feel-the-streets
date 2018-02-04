import enum
from .enums import BarrierType, RoofShape, BuildingType, FenceType, PowerSubstationType
from . import Named

class Locate(enum.Enum):
    kiosk = 0

class PowerSubstation(Named):
    type: PowerSubstationType = None
    location: str = None
    voltage: str = None
    frequency: int = None
    barrier: BarrierType = None
    building: BuildingType = None
    operator: str = None
    building_levels: int = None
    roof_shape: RoofShape = None
    building_colour: str = None
    height: int = None
    locate: Locate = None
    roof_colour: str = None
    fixme: str = None
    start_date: str = None
    note: str = None
    rating: str = None
    roof_levels: int = None
    gas_insulated: bool = None
    fence_type: FenceType = None
    access: bool = None
    low_voltage: int = None
    wikidata: str = None
    description: str = None
