import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from .enums import LeisureType, SportType, AccessType
from . import Addressable

class Leisure(Addressable):
    __tablename__ = "leisures"
    __mapper_args__ = {'polymorphic_identity': 'leisure'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    type = Column(Enum(LeisureType), nullable=False)
    sport = Column(Enum(SportType))
    surface = Column(UnicodeText)
    access = Column(Enum(AccessType))
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