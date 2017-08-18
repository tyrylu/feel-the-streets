import enum
from sqlalchemy import Column, Boolean, ForeignKey, Enum, Integer, UnicodeText
from .enums import AerialWayType, RoadType, RoofShape
from . import Named

class AerodromeType(enum.Enum):
    private = 0


class AerialWay(Named):
    __tablename__ = "aerialways"
    __mapper_args__ = {'polymorphic_identity': 'aerialway'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(AerialWayType), nullable=False)
    capacity = Column(Integer)
    occupancy = Column(Integer)
    duration = Column(Integer)
    wikipedia = Column(UnicodeText)
    building = Column(UnicodeText)
    length = Column(Integer)
    width = Column(Integer)
    heading = Column(UnicodeText)
    surface = Column(UnicodeText)
    aerodrome_type = Column(Enum(AerodromeType))
    icao = Column(UnicodeText)
    roof_shape = Column(Enum(RoofShape))
    heating = Column(Boolean)
    pedestrian = Column(Boolean)
    highway = Column(Enum(RoadType))
    bridge_structure = Column(UnicodeText)
    bridge = Column(Boolean)
    wikidata = Column(UnicodeText)