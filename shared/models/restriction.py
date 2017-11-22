import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, RestrictionType

class ExceptionType(enum.Enum):
    psv = 0
    bicycle = 1

class Restriction(Named):
    __tablename__ = "restrictions"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'restriction'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(RestrictionType))
    except_ = Column(UnicodeText) # Make it a list of ExceptionType
    note = Column(UnicodeText)
