from . import Named
from .enums import TrafficSignType

class Enforcement(Named):
    enforcement: TrafficSignType = None
    maxspeed: int = None