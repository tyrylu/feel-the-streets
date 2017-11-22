import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Amenity
from .enums import OSMObjectType

class CafeType(enum.Enum):
    tea_room = 0
class Cafe(Amenity):
    __tablename__ = "cafes"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["amenities.id", "amenities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'cafe'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    cafe_type = Column(IntEnum(CafeType))
    