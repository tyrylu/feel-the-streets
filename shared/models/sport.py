import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer
from ..sa_types import IntEnum
from .enums import SportType, OSMObjectType
from . import Named

class SwimmingType(enum.Enum):
    none = 0
    natural = 1

class Sport(Named):
    __tablename__ = "sports"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'sport'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(SportType), nullable=False)
    swimming = Column(IntEnum(SwimmingType))