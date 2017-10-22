import enum
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from .enums import CrossingType, BuildingType, RailWayType, TunnelType, BridgeType, Location, AccessType, BridgeStructure, OSMObjectType
from . import Named

class RailWayUsage(enum.Enum):
    unknown = 0
    main = 1
    branch = 2
    industrial = 3
    tourism = 4
    
class HazardType(enum.Enum):
    dangerous_junction = 1

class TrackClass(enum.Enum):
    C3 = 1
    D4 = 2

class StructureGauge(enum.Enum):
    GC = 1

class Bidirectionality(enum.Enum):
    regular = 1

class Colour(enum.Enum):
    green = 1
    red = 2

class SwitchType(enum.Enum):
    abt = 1

class RailWay(Named):
    __tablename__ = "rail_ways"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'rail_way'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(RailWayType), nullable=False)
    gauge = Column(UnicodeText)
    usage = Column(IntEnum(RailWayUsage))
    electrified = Column(UnicodeText)
    tracks = Column(Integer)
    maxspeed = Column(Integer)
    passenger_lines = Column(Integer)
    service = Column(UnicodeText)
    layer = Column(Integer)
    is_bridge = Column(IntEnum(BridgeType))
    tunnel = Column(IntEnum(TunnelType))
    fixme = Column(UnicodeText)
    ele = Column(Integer)
    crossing_light = Column(Boolean)
    crossing_bell = Column(Boolean)
    crossing_barrier = Column(Boolean)
    crossing_type = Column(IntEnum(CrossingType))
    supervised = Column(Boolean)
    surface = Column(UnicodeText)
    building_type = Column(IntEnum(BuildingType))
    flats = Column(Integer)
    levels = Column(Integer)
    oneway = Column(Boolean)
    tram_oneway = Column(Boolean)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    cutting = Column(Boolean)
    frequency = Column(Integer)
    voltage = Column(Integer)
    traffic_mode = Column(UnicodeText)
    preferred_direction = Column(UnicodeText)
    wheelchair = Column(Boolean)
    location = Column(IntEnum(Location))
    operator = Column(UnicodeText)
    bicycle = Column(Boolean)
    horse = Column(Boolean)
    hazard = Column(IntEnum(HazardType))
    alt_name = Column(UnicodeText)
    old_name = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    image = Column(UnicodeText) # Some Column(URL) would be more appropriate
    network = Column(UnicodeText)
    etcs = Column(UnicodeText)
    radio = Column(UnicodeText)
    track_class = Column(IntEnum(TrackClass))
    tilting_maxspeed = Column(Integer)
    structure_gauge = Column(IntEnum(StructureGauge))
    bidirectional = Column(IntEnum(Bidirectionality))
    ls = Column(Boolean)
    track_ref = Column(Integer)
    note = Column(UnicodeText)
    start_date = Column(UnicodeText)
    covered = Column(Boolean)
    description = Column(UnicodeText)
    embankment = Column(Boolean)
    proposed = Column(IntEnum(RailWayType))
    access = Column(IntEnum(AccessType))
    maxheight = Column(Float)
    disused = Column(IntEnum(RailWayType))
    abandoned_railway = Column(IntEnum(RailWayType))
    end_date = Column(UnicodeText)
    bridge_name = Column(UnicodeText)
    comment = Column(UnicodeText)
    colour = Column(IntEnum(Colour))
    station = Column(IntEnum(RailWayType))
    transport = Column(IntEnum(RailWayType))
    level = Column(Integer)
    construction = Column(IntEnum(RailWayType))
    foot = Column(Boolean)
    train = Column(Boolean)
    switch = Column(IntEnum(SwitchType))
    bridge_structure = Column(IntEnum(BridgeStructure))
    disused_railway = Column(IntEnum(RailWayType))
    loc_name = Column(UnicodeText)
    shelter = Column(Boolean)
    check_date = Column(UnicodeText) # Find a way how to parse the dates nicely