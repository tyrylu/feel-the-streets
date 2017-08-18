import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Float, Integer, UnicodeText
from .enums import CrossingType, TrafficCalmingType, RailWayType
from .entity import Entity

class BicycleType(enum.Enum):
    no = 0
    yes = 1
    dismount = 2

class KerbType(enum.Enum):
    lowered = 1
class TrafficSignalsType(enum.Enum):
    signals = 1
    signal = 2
class Crossing(Entity):
    __tablename__ = "crossings"
    __mapper_args__ = {'polymorphic_identity': 'crossing'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(Enum(CrossingType), nullable=False)
    name = Column(UnicodeText)
    button_operated = Column(Boolean)
    bicycle = Column(Enum(BicycleType))
    traffic_calming = Column(Enum(TrafficCalmingType))
    railway = Column(Enum(RailWayType))
    maxheight = Column(Float)
    foot = Column(Boolean)
    horse = Column(Boolean)
    kerb = Column(Enum(KerbType))
    segregated = Column(Boolean)
    traffic_signals = Column(Enum(TrafficSignalsType))