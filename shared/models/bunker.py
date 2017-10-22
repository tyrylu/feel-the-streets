import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

class BunkerType(enum.Enum):
    pillbox = 0

class Bunker(Named):
    __tablename__ = "bunkers"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'bunker'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    website = Column(UnicodeText)
    type = Column(IntEnum(BunkerType))
    historic = Column(Boolean)