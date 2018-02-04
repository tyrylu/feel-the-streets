import enum
from .enums import SportType, LeisureType, Surface, BarrierType, LandType, AccessType, ReservationType, GolfRelation, FenceType, ManMade
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
    type: SportType
    swimming: SwimmingType = None
    leisure: LeisureType = None
    surface: Surface = None
    layer: int = None
    barrier: BarrierType = None
    seasonal: bool = None
    wheelchair: bool = None
    landuse: LandType = None
    access: AccessType = None
    lit: bool = None
    operator: str = None
    abandoned: bool = None
    designation: str = None
    phone: str = None
    golf: GolfRelation = None
    fee: bool = None
    shooting: ShootingType = None
    # Separate entity?
    sport_1: SportType = None
    opening_hours_url: str = None
    reservation: ReservationType = None
    capacity: int = None
    fence_type: FenceType = None
    height: float = None
    facebook: str = None
    climbing_length: int = None
    official_name: str = None
    short_name: str = None
    url: str = None
    wikipedia: str = None
    climbing_sport: int = None
    old_name: str = None
    disused: bool = None
    alt_name_1: str = None
    man_made: ManMade = None
    fenced: bool = None
    wikimedia_commons: str = None
    covered: bool = None
    highjump: bool = None