import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

class TrafficSignType(enum.Enum):
    city_limit = 0
    maxspeed = 1

class TrafficSign(Named):
    __tablename__ = "traffic_signs"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'traffic_sign'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(TrafficSignType), nullable=False)
    alt_name = Column(UnicodeText)
    maxspeed = Column(Integer)