from . import OSMEntity
from .enums import BuildingType, Location, Material, PowerType

class Power(OSMEntity):
    type: PowerType
    building: BuildingType = None
    layer: int = None
    fixme: str = None
    location: Location = None
    high_voltage: int = None
    voltage: int = None
    low_voltage: int = None
    material: Material = None
    transition_location: bool = None
    tower: PowerType = None
    frequency: int = None
    area: bool = None
    operator: str = None