import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

class PlaceType(enum.Enum):
    village = 0
    hamlet = 1
    suburb = 2
    town = 3
    locality = 4
    city = 5
    neighbourhood = 6
    islet = 7
    island = 8
    square = 9
    farm = 10
    

class Place(Named):
    __tablename__ = "places"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'place'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(PlaceType), nullable=False)
    population = Column(Integer)
    wikipedia = Column(UnicodeText)
    is_in = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    ele = Column(Integer)