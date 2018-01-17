import enum
from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, RestrictionType

class ExceptionType(enum.Enum):
    psv = 0
    bicycle = 1

class Restriction(Named):
    __tablename__ = "restrictions"
    __mapper_args__ = {'polymorphic_identity': 'restriction', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(RestrictionType))
    except_ = Column(UnicodeText)
    # Make it a list of ExceptionType
    note = Column(UnicodeText)
    hgv_restriction = Column(IntEnum(RestrictionType))
    conditional = Column(UnicodeText)
