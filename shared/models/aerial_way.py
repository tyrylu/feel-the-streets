import enum
from sqlalchemy import Column, Boolean, ForeignKeyConstraint, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import AerialWayType, RoadType, RoofShape, BridgeStructure, OSMObjectType, AccessType, ManMade
from . import Named

class AerodromeType(enum.Enum):
    private = 0

class AerialWay(Named):
    __tablename__ = "aerialways"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'aerialway'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(AerialWayType), nullable=False)
    capacity = Column(Integer)
    occupancy = Column(Integer)
    duration = Column(Integer)
    wikipedia = Column(UnicodeText)
    building = Column(UnicodeText)
    length = Column(Integer)
    width = Column(Integer)
    heading = Column(UnicodeText)
    surface = Column(UnicodeText)
    aerodrome_type = Column(IntEnum(AerodromeType))
    icao = Column(UnicodeText)
    roof_shape = Column(IntEnum(RoofShape))
    heating = Column(Boolean)
    pedestrian = Column(Boolean)
    highway = Column(IntEnum(RoadType))
    bridge_structure = Column(IntEnum(BridgeStructure))
    bridge = Column(Boolean)
    wikidata = Column(UnicodeText)
    operator = Column(UnicodeText)
    is_in = Column(UnicodeText)
    maxweight = Column(Float)
    description = Column(UnicodeText)
    area = Column(Boolean)
    ele = Column(Float)
    start_date = Column(UnicodeText)
    height = Column(Float)
    layer = Column(Integer)
    note = Column(UnicodeText)
    access = Column(IntEnum(AccessType))
    lit = Column(Boolean)
    navigationaid = Column(UnicodeText)
    man_made = Column(IntEnum(ManMade))
    frequency = Column(UnicodeText)
    