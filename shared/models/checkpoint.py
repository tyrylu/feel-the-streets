import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from . import Named

class CheckpointType(enum.Enum):
    hiking = 0

class CheckpointKind(enum.Enum):
    needler = 0

class Checkpoint(Named):
    __tablename__ = "checkpoints"
    __mapper_args__ = {'polymorphic_identity': 'checkpoint'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(CheckpointType), nullable=False)
    checkpoint_type = Column(Enum(CheckpointKind))
    note = Column(UnicodeText)
    checkpoint_name = Column(UnicodeText)