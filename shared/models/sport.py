import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import SportType, OSMObjectType, LeisureType, Surface, BarrierType, LandType, AccessType, ReservationType, GolfRelation
from . import Addressable

class SwimmingType(enum.Enum):
    none = 0
    natural = 1
class ShootingType(enum.Enum):
    indoor_range = 0
    lasertag = 1
class Sport(Addressable):
    __tablename__ = "sports"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["addressables.id", "addressables.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'sport'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(SportType), nullable=False)
    swimming = Column(IntEnum(SwimmingType))
    leisure = Column(IntEnum(LeisureType))
    surface = Column(IntEnum(Surface))
    layer = Column(Integer)
    barrier = Column(IntEnum(BarrierType))
    seasonal = Column(Boolean)
    wheelchair = Column(Boolean)
    landuse = Column(IntEnum(LandType))
    opening_hours = Column(UnicodeText)
    access = Column(IntEnum(AccessType))
    lit = Column(Boolean)
    operator = Column(UnicodeText)
    abandoned = Column(Boolean)
    designation = Column(UnicodeText)
    phone = Column(UnicodeText)
    golf = Column(IntEnum(GolfRelation))
    fee = Column(Boolean)
    shooting = Column(IntEnum(ShootingType)) # Separate entity?
    sport_1 = Column(IntEnum(SportType))
    email = Column(UnicodeText)
    opening_hours_url = Column(UnicodeText)
    reservation = Column(IntEnum(ReservationType))
    capacity = Column(Integer)