import enum
from . import Named
from .enums import RouteType, Location

class WireType(enum.Enum):
    unknown = 0
    single = 1
    double = 2
    triple = 3

class PowerLineType(enum.Enum):
    bay = 0
    busbar = 1
    route = 2
    
class PowerLine(Named):
    type: PowerLineType = None
    cables: int = None
    voltage: int = None
    wires: WireType = None
    frequency: int = None
    operator: str = None
    note: str = None
    route: RouteType = None
    layer: int = None
    location: Location = None
    circuits: int = None
    line_colour: str = None
    colour: str = None
    description: str = None
    complete: bool = None
    fixme: str = None



    @property
    def effective_width(self):
        return 0