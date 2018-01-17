import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, TowerType

class BunkerType(enum.Enum):
    pillbox = 0

class Bunker(Named):
    __tablename__ = "bunkers"
    __mapper_args__ = {'polymorphic_identity': 'bunker', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    website = Column(UnicodeText)
    type = Column(IntEnum(BunkerType))
    historic = Column(Boolean)
    height = Column(Integer)
    tower_type = Column(IntEnum(TowerType))
