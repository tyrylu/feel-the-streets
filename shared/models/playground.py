import enum
from sqlalchemy import Column, ForeignKey, Integer
from ..sa_types import IntEnum
from .leisure import Leisure
from .enums import OSMObjectType, Material

class PlaygroundType(enum.Enum):
    sandpit = 0
    slide = 1
    swing = 2
    basketswing = 3
    climbingframe = 4
    roundabout = 5
    balancebeam = 6

class Playground(Leisure):
    __tablename__ = "playgrounds"
    __mapper_args__ = {'polymorphic_identity': 'playground', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("leisures.id"), primary_key=True)
    playground_type = Column(IntEnum(PlaygroundType))
    material = Column(IntEnum(Material))
