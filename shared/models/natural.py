import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import ManMade, TourismType, NaturalType, OSMObjectType
from . import Named

class Natural(Named):
    __tablename__ = "naturals"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'natural'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(NaturalType), nullable=False)
    lining = Column(UnicodeText)
    man_made = Column(IntEnum(ManMade))
    depth = Column(Float)
    ele = Column(Float)
    note = Column(UnicodeText)
    drinking_water = Column(Boolean)
    alt_name = Column(UnicodeText)
    website = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    inscription = Column(UnicodeText)
    tourism_type = Column(IntEnum(TourismType))
    opening_hours = Column(UnicodeText)
    surface = Column(UnicodeText)
    material = Column(UnicodeText)
    wikidata = Column(UnicodeText)