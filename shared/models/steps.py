import enum
from sqlalchemy import Column, ForeignKey, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import AccessType, Location, OSMObjectType, SidewalkType, TrailVisibility, Service

class StepsDirection(enum.Enum):
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
    flat = 1

class StepLength(enum.Enum):
    normal = 0
    short = 1

class HandrailType(enum.Enum):
    no = 0
    yes = 1
    left = 2
    right = 3
    both = 4

class Steps(Named):
    __tablename__ = "steps"
    __mapper_args__ = {'polymorphic_identity': 'steps', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    direction = Column(IntEnum(StepsDirection))
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
    motorcar = Column(Boolean)
    winter_service = Column(Boolean)
    cutting = Column(Boolean)

