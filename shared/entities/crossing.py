import enum
from .enums import CrossingType, TrafficCalmingType, RailWayType, KerbType, CurbType, BicycleType, RoadType, BarrierType, ParkingLaneType
from . import OSMEntity

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

class Crossing(OSMEntity):
    type: CrossingType
    name: str = None
    button_operated: bool = None
    bicycle: BicycleType = None
    traffic_calming: TrafficCalmingType = None
    railway: RailWayType = None
    maxheight: float = None
    foot: bool = None
    horse: bool = None
    kerb: KerbType = None
    segregated: bool = None
    traffic_signals: TrafficSignalsType = None
    tactile_paving: bool = None
    note: str = None
    lit: bool = None
    sloped_curb: CurbType = None
    wheelchair: bool = None
    maxspeed: int = None
    traffic_signals_direction: TrafficSignalsDirection = None
    traffic_signals_sound: bool = None
    supervised: bool = None
    smoothness: str = None
    surface: str = None
    fixme: str = None
    inscription: str = None
    cycleway: CicleWayKind = None
    sound: bool = None
    direction: TrafficSignalsDirection = None
    level: int = None
    traffic_sign: RoadType = None
    barrier: BarrierType = None
    both_parking_lane: ParkingLaneType = None
    short_name: str = None
    highway_2: RoadType = None