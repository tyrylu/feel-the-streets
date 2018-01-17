import enum
from sqlalchemy import Column, ForeignKey, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import SportType, OSMObjectType, LeisureType, Surface, BarrierType, LandType, AccessType, ReservationType, GolfRelation, FenceType, ManMade
from . import Addressable

class SwimmingType(enum.Enum):
    none = 0
    natural = 1

class ShootingType(enum.Enum):
    indoor_range = 0
    lasertag = 1
    range = 2
    paintball = 3

class Sport(Addressable):
    __tablename__ = "sports"
    __mapper_args__ = {'polymorphic_identity': 'sport', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    type = Column(IntEnum(SportType), nullable=False)
    swimming = Column(IntEnum(SwimmingType))
    leisure = Column(IntEnum(LeisureType))
    surface = Column(IntEnum(Surface))
    layer = Column(Integer)
    barrier = Column(IntEnum(BarrierType))
    seasonal = Column(Boolean)
    wheelchair = Column(Boolean)
    landuse = Column(IntEnum(LandType))
    access = Column(IntEnum(AccessType))
    lit = Column(Boolean)
    operator = Column(UnicodeText)
    abandoned = Column(Boolean)
    designation = Column(UnicodeText)
    phone = Column(UnicodeText)
    golf = Column(IntEnum(GolfRelation))
    fee = Column(Boolean)
    shooting = Column(IntEnum(ShootingType))
    # Separate entity?
    sport_1 = Column(IntEnum(SportType))
    opening_hours_url = Column(UnicodeText)
    reservation = Column(IntEnum(ReservationType))
    capacity = Column(Integer)
    fence_type = Column(IntEnum(FenceType))
    height = Column(Float)
    facebook = Column(UnicodeText)
    climbing_length = Column(Integer)
    official_name = Column(UnicodeText)
    short_name = Column(UnicodeText)
    url = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    climbing_sport = Column(Integer)
    old_name = Column(UnicodeText)
    disused = Column(Boolean)
    alt_name_1 = Column(UnicodeText)
    man_made = Column(IntEnum(ManMade))
    fenced = Column(Boolean)
    wikimedia_commons = Column(UnicodeText)
    covered = Column(Boolean)
    highjump = Column(Boolean)
