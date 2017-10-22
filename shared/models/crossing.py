import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import CrossingType, TrafficCalmingType, RailWayType, OSMObjectType
from .entity import Entity

class BicycleType(enum.Enum):
    no = 0
    yes = 1
    dismount = 2
    designated = 3

class KerbType(enum.Enum):
    lowered = 1

class TrafficSignalsType(enum.Enum):
    signals = 1
    signal = 2
    blinker = 3
    pedestrian = 4

class CurbType(enum.Enum):
        no = 0
        yes = 1
        both = 2

class TrafficSignalsDirection(enum.Enum):
    forward = 1
    backward = 2

class CicleWayKind(enum.Enum):
    asl = 1

class Crossing(Entity):
    __tablename__ = "crossings"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'crossing'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
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
    