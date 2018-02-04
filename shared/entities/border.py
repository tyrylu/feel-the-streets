import enum
from .boundary import Boundary
from .enums import WaterWayType

class BorderType(enum.Enum):
    nation = 0

class Border(Boundary):
    border_type: BorderType = None
    is_in: str = None
    left_country: str = None
    right_country: str = None
    uploaded_by: str = None
    waterway: WaterWayType = None
    boat: bool = None
    layer: int = None