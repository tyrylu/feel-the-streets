import enum
from . import Named
from .enums import BuildingType, WheelchairAccess, BicycleType

class TransportRelationship(enum.Enum):
    none = 0
    platform = 1
    tram_stop = 2
    platform_edge = 3
    
class Platform(Named):
    train: bool = None
    bus: bool = None
    tram: bool = None
    railway: TransportRelationship = None
    shelter: bool = None
    bench: bool = None
    network: str = None
    operator: str = None
    surface: str = None
    lit: bool = None
    wheelchair: WheelchairAccess = None
    covered: bool = None
    building: BuildingType = None
    bin: bool = None
    official_name: str = None
    area: bool = None
    foot: bool = None
    layer: int = None
    trolleybus: bool = None
    tunnel: bool = None
    route_ref: str = None
    bridge: bool = None
    tactile_paving: bool = None
    short_name: str = None
    alt_name: str = None
    fixme: str = None
    note: str = None
    description: str = None
    level: int = None
    bicycle: BicycleType = None
    subway: bool = None
    width: int = None
    local_ref: str = None
    indoor_level: str = None
