import enum
from . import Named
from .enums import TowerType

class BunkerType(enum.Enum):
    pillbox = 0

class Bunker(Named):
    website: str = None
    type: BunkerType = None
    historic: bool = None
    height: int = None
    tower_type: TowerType = None