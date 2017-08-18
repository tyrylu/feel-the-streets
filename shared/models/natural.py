import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Float, Integer, UnicodeText
from .enums import ManMade, TourismType, NaturalType
from . import Named

class Natural(Named):
    __tablename__ = "naturals"
    __mapper_args__ = {'polymorphic_identity': 'natural'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(NaturalType), nullable=False)
    lining = Column(UnicodeText)
    man_made = Column(Enum(ManMade))
    depth = Column(Float)
    ele = Column(Float)
    note = Column(UnicodeText)
    drinking_water = Column(Boolean)
    alt_name = Column(UnicodeText)
    website = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    inscription = Column(UnicodeText)
    tourism_type = Column(Enum(TourismType))
    opening_hours = Column(UnicodeText)
    surface = Column(UnicodeText)
    material = Column(UnicodeText)
    wikidata = Column(UnicodeText)