import enum
from . import Amenity

class CafeType(enum.Enum):
    tea_room = 0

class Cafe(Amenity):
    cafe_type: CafeType = None
    