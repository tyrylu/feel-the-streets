import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Float, Integer, UnicodeText
from . import Named
from .enums import AccessType, Location

class Direction(enum.Enum):
    unknown = 0
    up = 1
    down = 2

class Steps(Named):
    __tablename__ = "steps"
    __mapper_args__ = {'polymorphic_identity': 'steps'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    direction = Column(Enum(Direction))
    step_count = Column(Integer)
    surface = Column(UnicodeText)
    width = Column(Float)
    bicycles_allowed = Column(Boolean)
    lit = Column(Boolean)
    layer = Column(Integer)
    foot = Column(Enum(AccessType))
    tunnel = Column(UnicodeText)
    access = Column(Enum(AccessType))
    motor_vehicle = Column(Enum(AccessType))
    handrail = Column(Boolean)
    vehicle = Column(Boolean)
    bicycle = Column(Boolean)
    ramp = Column(Boolean)
    horse = Column(Boolean)
    sac_scale = Column(UnicodeText)
    fixme = Column(UnicodeText)
    note = Column(UnicodeText)
    material = Column(UnicodeText)
    tracktype = Column(UnicodeText)
    location = Column(Enum(Location))