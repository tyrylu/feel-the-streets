import enum
from . import Named
from .enums import WheelchairAccess, AccessType, EntranceType, MilitaryType

class DoorType(enum.Enum):
    yes = 0
    overhead = 1
    hinged = 2
    rotating = 3

class Entrance(Named):
    type: EntranceType
    level: int = None
    bicycle: bool = None
    foot: bool = None
    wheelchair: WheelchairAccess = None
    horse: bool = None
    motorcar: bool = None
    motorcycle: bool = None
    access: AccessType = None
    door: DoorType = None
    note: str = None
    description: str = None
    military: MilitaryType = None
    fixme: str = None