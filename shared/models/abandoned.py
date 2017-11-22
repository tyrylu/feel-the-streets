import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, AccessType

class AbandonedType(enum.Enum):
    path = 0
    unclassified = 1

class Abandoned(Named):
    __tablename__ = "abandoned"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'abandoned'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(AbandonedType))
    bicycle = Column(IntEnum(AccessType))
    