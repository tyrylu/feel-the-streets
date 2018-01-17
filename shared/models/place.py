import enum
from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, PlaceType, AttractionType, LeisureType, LandType

class Place(Named):
    __tablename__ = "places"
    __mapper_args__ = {'polymorphic_identity': 'place', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(PlaceType), nullable=False)
    population = Column(Integer)
    wikipedia = Column(UnicodeText)
    is_in = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    ele = Column(Integer)
    loc_name = Column(UnicodeText)
    old_name = Column(UnicodeText)
    postal_code = Column(UnicodeText)
    alt_name = Column(UnicodeText)
    alt_name_de = Column(UnicodeText)
    website = Column(UnicodeText)
    email = Column(UnicodeText)
    phone = Column(UnicodeText)
    note = Column(UnicodeText)
    sorting_name = Column(UnicodeText)
    short_name = Column(UnicodeText)
    attraction = Column(IntEnum(AttractionType))
    leisure = Column(IntEnum(LeisureType))
    landuse = Column(IntEnum(LandType))
    start_date = Column(Integer)
    int_name = Column(UnicodeText)
    wikipedia_cs = Column(UnicodeText)
    alt_name_cs = Column(UnicodeText)

