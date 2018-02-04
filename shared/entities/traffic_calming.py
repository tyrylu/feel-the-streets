from .enums import TrafficCalmingType, Surface, AccessType
from . import OSMEntity

class TrafficCalming(OSMEntity):
    type: TrafficCalmingType
    note: str = None
    surface: Surface = None
    maxspeed: int = None
    level: int = None
    fixme: str = None
    bicycle: AccessType = None