from . import Named
from .enums import TrafficSignType

class TrafficSign(Named):
    type: TrafficSignType
    alt_name: str = None
    maxspeed: int = None
    backward: bool = None