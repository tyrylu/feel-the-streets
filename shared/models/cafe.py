import enum
from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Amenity
from .enums import OSMObjectType

class CafeType(enum.Enum):
    tea_room = 0

class Cafe(Amenity):
    __tablename__ = "cafes"
    __mapper_args__ = {'polymorphic_identity': 'cafe', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("amenities.id"), primary_key=True)
    cafe_type = Column(IntEnum(CafeType))
    