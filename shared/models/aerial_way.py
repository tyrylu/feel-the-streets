import enum
from sqlalchemy import Column, Boolean, ForeignKey, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import AerialWayType, RoadType, RoofShape, BridgeStructure, OSMObjectType, AccessType, ManMade, BarrierType
from . import Named

class AerodromeType(enum.Enum):
    private = 0
    international = 1

class Subtype(enum.Enum):
    gp = 0
    loc = 1

class BeaconType(enum.Enum):
    ILS = 0

class RunwayType(enum.Enum):
    blast_pad = 0

class MilitaryRelationship(enum.Enum):
    airfield = 0

class AirMarkType(enum.Enum):
    beacon = 0

class AerialWay(Named):
    __tablename__ = "aerialways"
    __mapper_args__ = {'polymorphic_identity': 'aerialway', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
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
    disused_aeroway = Column(IntEnum(AerialWayType))
    subtype = Column(IntEnum(Subtype))
    note_cs = Column(UnicodeText)
    oneway = Column(Boolean)
    proposed = Column(IntEnum(AerialWayType))
    beacon_type = Column(IntEnum(BeaconType))
    runway = Column(IntEnum(RunwayType))
    barrier = Column(IntEnum(BarrierType))
    email = Column(UnicodeText)
    phone = Column(UnicodeText)
    military = Column(IntEnum(MilitaryRelationship))
    loc_name = Column(UnicodeText)
    min_height = Column(Integer)
    emergency = Column(Boolean)
    building_levels = Column(Integer)
    airmark = Column(IntEnum(AirMarkType))
    iata = Column(UnicodeText)

