import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from . import Named

class PlaceType(enum.Enum):
    village = 0
    hamlet = 1
    suburb = 2
    town = 3
    locality = 4
    city = 5
    neighbourhood = 6
    islet = 7

class Place(Named):
    __tablename__ = "places"
    __mapper_args__ = {'polymorphic_identity': 'place'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(PlaceType), nullable=False)
    population = Column(Integer)
    wikipedia = Column(UnicodeText)
    is_in = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    ele = Column(Integer)