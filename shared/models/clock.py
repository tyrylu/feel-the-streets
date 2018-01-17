import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Amenity
from .enums import OSMObjectType, TourismType, SupportType, EntranceType

class DisplayType(enum.Enum):
    none = 0
    sundial = 1
    analog = 2
    digital = 3
    unorthodox = 4

class ClockVisibility(enum.Enum):
    area = 0
    street = 1
    house = 2

class Clock(Amenity):
    __tablename__ = "clocks"
    __mapper_args__ = {'polymorphic_identity': 'clock', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("amenities.id"), primary_key=True)
    display = Column(IntEnum(DisplayType))
    support = Column(IntEnum(SupportType))
    faces = Column(Integer)
    visibility = Column(IntEnum(ClockVisibility))
    barometer = Column(Boolean)
    date = Column(Boolean)
    hygrometer = Column(Boolean)
    thermometer = Column(Boolean)
    tourism = Column(IntEnum(TourismType))
    inscription = Column(UnicodeText)
    artist_name = Column(UnicodeText)
    entrance = Column(IntEnum(EntranceType))
