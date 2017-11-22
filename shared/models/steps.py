import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import AccessType, Location, OSMObjectType, SidewalkType

class Direction(enum.Enum):
    unknown = 0
    up = 1
    down = 2
    yes = 3

class StepCondition(enum.Enum):
    even = 0
    uneven = 1
    rough = 2
class StepHeight(enum.Enum):
    normal = 0

class StepLength(enum.Enum):
    normal = 0

class TrailVisibility(enum.Enum):
    excellent = 0
    good = 1

class HandrailType(enum.Enum):
    no = 0
    yes = 1
    left = 2
    right = 3
    both = 4

class Service(enum.Enum):
    alley = 0
    parking_aisle = 1

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
    handrail = Column(IntEnum(HandrailType))
    vehicle = Column(Boolean)
    bicycle = Column(IntEnum(AccessType))
    ramp = Column(Boolean)
    horse = Column(Boolean)
    sac_scale = Column(UnicodeText)
    fixme = Column(UnicodeText)
    note = Column(UnicodeText)
    material = Column(UnicodeText)
    tracktype = Column(UnicodeText)
    location = Column(IntEnum(Location))
    wheelchair = Column(Boolean)
    conveying = Column(Boolean)
    level = Column(UnicodeText)
    mtb_scale = Column(Integer)
    mtb_scale_uphill = Column(Integer)
    bridge = Column(Boolean)
    left_handrail = Column(Boolean)
    right_handrail = Column(Boolean)
    center_handrail = Column(Boolean)
    step_condition = Column(IntEnum(StepCondition))
    tactile_paving = Column(Boolean)
    trail_visibility = Column(IntEnum(TrailVisibility))
    start_date = Column(UnicodeText)
    covered = Column(Boolean)
    escalator = Column(Boolean)
    sidewalk = Column(IntEnum(SidewalkType))
    service = Column(IntEnum(Service))
    step_height = Column(IntEnum(StepHeight))
    step_length = Column(IntEnum(StepLength))
    