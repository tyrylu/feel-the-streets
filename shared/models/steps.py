import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import AccessType, Location, OSMObjectType

class Direction(enum.Enum):
    unknown = 0
    up = 1
    down = 2
    yes = 3

class Steps(Named):
    __tablename__ = "steps"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'steps'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    direction = Column(IntEnum(Direction))
    step_count = Column(Integer)
    surface = Column(UnicodeText)
    width = Column(Float)
    bicycles_allowed = Column(Boolean)
    lit = Column(Boolean)
    layer = Column(Integer)
    foot = Column(IntEnum(AccessType))
    tunnel = Column(UnicodeText)
    access = Column(IntEnum(AccessType))
    motor_vehicle = Column(IntEnum(AccessType))
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
    location = Column(IntEnum(Location))
    wheelchair = Column(Boolean)