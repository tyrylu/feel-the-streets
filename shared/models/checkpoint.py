import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

class CheckpointType(enum.Enum):
    hiking = 0

class CheckpointKind(enum.Enum):
    needler = 0

class Checkpoint(Named):
    __tablename__ = "checkpoints"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'checkpoint'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(CheckpointType), nullable=False)
    checkpoint_type = Column(IntEnum(CheckpointKind))
    note = Column(UnicodeText)
    checkpoint_name = Column(UnicodeText)