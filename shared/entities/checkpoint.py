import enum
from . import Named

class CheckpointType(enum.Enum):
    hiking = 0

class CheckpointKind(enum.Enum):
    needler = 0

class Checkpoint(Named):
    type: CheckpointType
    checkpoint_type: CheckpointKind = None
    note: str = None
    checkpoint_name: str = None