import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum, DimensionalFloat
from .enums import LeisureType, SportType, AccessType, OSMObjectType, BarrierType, FenceType, IndoorType, InternetAccess
from . import Addressable

class Leisure(Addressable):
    __tablename__ = "leisures"
    __mapper_args__ = {'polymorphic_identity': 'leisure', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    type = Column(IntEnum(LeisureType), nullable=False)
    sport = Column(IntEnum(SportType))
    surface = Column(UnicodeText)
    access = Column(IntEnum(AccessType))
    designation = Column(UnicodeText)
    openfire = Column(Boolean)
    backrest = Column(Boolean)
    dogs_allowed = Column(Boolean)
    layer = Column(Integer)
    wikipedia = Column(UnicodeText)
    phone = Column(UnicodeText)
    operator = Column(UnicodeText)
    hoops = Column(Integer)
    high_jump = Column(Boolean)
    pole_vault = Column(Boolean)
    long_jump = Column(Boolean)
    shot_put = Column(Boolean)
    covered = Column(Boolean)
    old_name = Column(UnicodeText)
    barrier = Column(IntEnum(BarrierType))
    fence_type = Column(IntEnum(FenceType))
    wheelchair = Column(Boolean)
    entrance = Column(Boolean)
    baby = Column(Boolean)
    sorting_name = Column(UnicodeText)
    fee = Column(Boolean)
    fenced = Column(Boolean)
    height = Column(DimensionalFloat("meter"))
    lit = Column(Boolean)
    facebook = Column(UnicodeText)
    small_boats = Column(Boolean)
    google_plus = Column(UnicodeText)
    indoor = Column(IntEnum(IndoorType))
    alt_name_1 = Column(UnicodeText)
    start_date = Column(UnicodeText)
    alt_name_2 = Column(UnicodeText)
    short_name = Column(UnicodeText)

