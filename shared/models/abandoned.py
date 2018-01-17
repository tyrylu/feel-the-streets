import enum
from sqlalchemy import Column, ForeignKey, Integer
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, AccessType

class AbandonedType(enum.Enum):
    path = 0
    unclassified = 1
    steps = 2

class Abandoned(Named):
    __tablename__ = "abandoned"
    __mapper_args__ = {'polymorphic_identity': 'abandoned', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(AbandonedType))
    bicycle = Column(IntEnum(AccessType))
    
