import enum
from . import Named
from .enums import AccessType

class AbandonedType(enum.Enum):
    path = 0
    unclassified = 1
    steps = 2

class Abandoned(Named):
    type: AbandonedType = None
    bicycle: AccessType = None
    