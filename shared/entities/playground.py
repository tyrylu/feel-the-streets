import enum
from .leisure import Leisure
from .enums import Material

class PlaygroundType(enum.Enum):
    sandpit = 0
    slide = 1
    swing = 2
    basketswing = 3
    climbingframe = 4
    roundabout = 5
    balancebeam = 6

class Playground(Leisure):
    playground_type: PlaygroundType = None
    material: Material = None