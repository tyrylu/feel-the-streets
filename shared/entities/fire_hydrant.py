import enum
from . import OSMEntity

class FireHydrantType(enum.Enum):
    unknown = 0
    pillar = 1
    wall = 2
    underground = 3

class FireHydrantPosition(enum.Enum):
    sidewalk = 0
    green = 1
    street = 2

class FireHydrant(OSMEntity):
    type: FireHydrantType
    position: FireHydrantPosition = None
    count: int = None