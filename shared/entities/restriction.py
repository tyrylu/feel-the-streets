import enum
from . import Named
from .enums import RestrictionType

class ExceptionType(enum.Enum):
    psv = 0
    bicycle = 1

class Restriction(Named):
    type: RestrictionType = None
    except_: str = None
    # Make it a list of ExceptionType
    note: str = None
    hgv_restriction: RestrictionType = None
    conditional: str = None