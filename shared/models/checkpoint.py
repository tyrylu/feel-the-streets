import enum
from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

class CheckpointType(enum.Enum):
    hiking = 0

class CheckpointKind(enum.Enum):
    needler = 0

class Checkpoint(Named):
    __tablename__ = "checkpoints"
    __mapper_args__ = {'polymorphic_identity': 'checkpoint', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(CheckpointType), nullable=False)
    checkpoint_type = Column(IntEnum(CheckpointKind))
    note = Column(UnicodeText)
    checkpoint_name = Column(UnicodeText)