import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import LeisureType, SportType, AccessType, OSMObjectType, BarrierType, FenceType
from . import Addressable

class Leisure(Addressable):
    __tablename__ = "leisures"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["addressables.id", "addressables.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'leisure'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(LeisureType), nullable=False)
    sport = Column(IntEnum(SportType))
    surface = Column(UnicodeText)
    access = Column(IntEnum(AccessType))
    description = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    designation = Column(UnicodeText)
    openfire = Column(Boolean)
    backrest = Column(Boolean)
    dogs_allowed = Column(Boolean)
    layer = Column(Integer)
    wikipedia = Column(UnicodeText)
    email = Column(UnicodeText)
    phone = Column(UnicodeText)
    operator = Column(UnicodeText)
    hoops = Column(Integer)
    high_jump = Column(Boolean)
    pole_vault = Column(Boolean)
    long_jump = Column(Boolean)
    shot_put = Column(Boolean)
    covered = Column(Boolean)
    wikidata = Column(UnicodeText)
    old_name = Column(UnicodeText)
    barrier = Column(IntEnum(BarrierType))
    fence_type = Column(IntEnum(FenceType))
    wheelchair = Column(Boolean)
    entrance = Column(Boolean)
    baby = Column(Boolean)
    