import enum
from . import Amenity
from .enums import TourismType, SupportType, EntranceType

class DisplayType(enum.Enum):
    none = 0
    sundial = 1
    analog = 2
    digital = 3
    unorthodox = 4

class ClockVisibility(enum.Enum):
    area = 0
    street = 1
    house = 2

class Clock(Amenity):
    display: DisplayType = None
    support: SupportType = None
    faces: int = None
    visibility: ClockVisibility = None
    barometer: bool = None
    date: bool = None
    hygrometer: bool = None
    thermometer: bool = None
    tourism: TourismType = None
    inscription: str = None
    artist_name: str = None
    entrance: EntranceType = None