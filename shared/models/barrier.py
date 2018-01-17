import enum
from sqlalchemy import Column, ForeignKey, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum, DimensionalFloat
from .enums import BarrierType, AccessType, ManMade, OSMObjectType, TrafficCalmingType, KerbType, RoadType, BridgeStructure, RailWayType, Service
from . import Named

class BollardType(enum.Enum):
    rising = 1
    removable = 2
    yes = 3
    irremovable = 4

class WallType(enum.Enum):
    gabion = 0
    brick = 1
    noise_barrier = 2
    dry_stone = 3
    flood_wall = 4
    jersey_barrier = 5
    retaining_wall = 6

class StileType(enum.Enum):
    ladder = 0
    stepover = 1
    
class LiftgateType(enum.Enum):
    double = 0
    single = 1

class LeafType(enum.Enum):
    needleleaved = 0
    broadleaved = 1

class SwingGateType(enum.Enum):
    single = 0

class Barrier(Named):
    __tablename__ = "barriers"
    __mapper_args__ = {'polymorphic_identity': 'barrier', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(BarrierType), nullable=False)
    foot = Column(IntEnum(AccessType))
    bicycle = Column(IntEnum(AccessType))
    vehicle = Column(IntEnum(AccessType))
    horse = Column(Boolean)
    access = Column(IntEnum(AccessType))
    entrance = Column(UnicodeText)
    motor_vehicle = Column(UnicodeText)
    note = Column(UnicodeText)
    maxwidth = Column(Integer)
    fence_type = Column(UnicodeText)
    height = Column(DimensionalFloat("meter"))
    material = Column(UnicodeText)
    motorcar = Column(IntEnum(AccessType))
    motorcycle = Column(Boolean)
    toll = Column(Boolean)
    operator = Column(UnicodeText)
    toll_hgv = Column(Boolean)
    opening_hours = Column(UnicodeText)
    bollard = Column(IntEnum(BollardType))
    destination = Column(Boolean)
    noexit = Column(Boolean)
    ticks = Column(Integer)
    man_made = Column(IntEnum(ManMade))
    description = Column(UnicodeText)
    fixme = Column(UnicodeText)
    two_sided = Column(Boolean)
    historic = Column(Boolean)
    complete = Column(Boolean)
    layer = Column(Integer)
    wall = Column(IntEnum(WallType))
    # Create subclass?
    stile = Column(IntEnum(StileType))
    # Subclass?
    traffic_calming = Column(IntEnum(TrafficCalmingType))
    level = Column(Integer)
    wheelchair = Column(Boolean)
    liftgate_type = Column(IntEnum(LiftgateType))
    maxheight = Column(Float)
    wikidata = Column(UnicodeText)
    fee = Column(UnicodeText)
    alt_name = Column(UnicodeText)
    kerb = Column(IntEnum(KerbType))
    disused = Column(Boolean)
    width = Column(Float)
    leaf_type = Column(IntEnum(LeafType))
    colour = Column(UnicodeText)
    building_colour = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    hgv = Column(Boolean)
    website = Column(UnicodeText)
    count = Column(Integer)
    network = Column(UnicodeText)
    state = Column(IntEnum(BarrierType))
    sorting_name = Column(UnicodeText)
    abandoned_highway = Column(IntEnum(RoadType))
    bridge_structure = Column(IntEnum(BridgeStructure))
    stroller = Column(Boolean)
    pedestrians = Column(IntEnum(AccessType))
    mofa = Column(Boolean)
    ford = Column(Boolean)
    disused_railway = Column(IntEnum(RailWayType))
    service = Column(IntEnum(Service))
    goods = Column(Boolean)
    comment = Column(UnicodeText)
    agricultural = Column(Boolean)
    swing_gate_type = Column(IntEnum(SwingGateType))
