import enum
from . import Named

class Ant(enum.Enum):
    rxtx = 0
    tx = 1

class RFCategory(enum.Enum):
    tv = 0
    HAM = 1
    ais = 2
    radio = 3

class RF(Named):
    ant: Ant = None
    category: RFCategory = None
    modulation: str = None
    power: int = None
    content: str = None
    stereo: bool = None
    pi: str = None
    dvbt_parameters: str = None
    owner: str = None
    callsign: str = None