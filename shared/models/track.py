from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from . import Road
from .enums import Inclination, LeisureType, SportType

class Track(Road):
    __tablename__ = "tracks"
    __mapper_args__ = {'polymorphic_identity': 'track'}
    id = Column(Integer, ForeignKey("roads.id"), primary_key=True)
    motorcar_allowed = Column(Boolean)
    leisure = Column(Enum(LeisureType))
    sport = Column(Enum(SportType))
    website = Column(UnicodeText)
    mtb_scale = Column(Integer)
    mtb_scale_uphill = Column(Integer)