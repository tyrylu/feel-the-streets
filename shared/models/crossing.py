import enum
from sqlalchemy import Column, ForeignKey, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import CrossingType, TrafficCalmingType, RailWayType, OSMObjectType, KerbType, CurbType, BicycleType, RoadType, BarrierType, ParkingLaneType
from .entity import Entity

class TrafficSignalsType(enum.Enum):
    signals = 1
    signal = 2
    blinker = 3
    pedestrian = 4
    emergency = 5

class TrafficSignalsDirection(enum.Enum):
    forward = 1
    backward = 2

class CicleWayKind(enum.Enum):
    asl = 1

class Crossing(Entity):
    __tablename__ = "crossings"
    __mapper_args__ = {'polymorphic_identity': 'crossing', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(IntEnum(CrossingType), nullable=False)
    name = Column(UnicodeText)
    button_operated = Column(Boolean)
    bicycle = Column(IntEnum(BicycleType))
    traffic_calming = Column(IntEnum(TrafficCalmingType))
    railway = Column(IntEnum(RailWayType))
    maxheight = Column(Float)
    foot = Column(Boolean)
    horse = Column(Boolean)
    kerb = Column(IntEnum(KerbType))
    segregated = Column(Boolean)
    traffic_signals = Column(IntEnum(TrafficSignalsType))
    tactile_paving = Column(Boolean)
    note = Column(UnicodeText)
    lit = Column(Boolean)
    sloped_curb = Column(IntEnum(CurbType))
    wheelchair = Column(Boolean)
    maxspeed = Column(Integer)
    traffic_signals_direction = Column(IntEnum(TrafficSignalsDirection))
    traffic_signals_sound = Column(Boolean)
    supervised = Column(Boolean)
    smoothness = Column(UnicodeText)
    surface = Column(UnicodeText)
    fixme = Column(UnicodeText)
    inscription = Column(UnicodeText)
    cycleway = Column(IntEnum(CicleWayKind))
    sound = Column(Boolean)
    direction = Column(IntEnum(TrafficSignalsDirection))
    level = Column(Integer)
    traffic_sign = Column(IntEnum(RoadType))
    barrier = Column(IntEnum(BarrierType))
    both_parking_lane = Column(IntEnum(ParkingLaneType))
    short_name = Column(UnicodeText)
    highway_2 = Column(IntEnum(RoadType))
