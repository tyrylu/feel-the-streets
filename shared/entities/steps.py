import enum
from . import Named
from .enums import AccessType, Location, SidewalkType, TrailVisibility, Service

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
    direction: StepsDirection = None
    step_count: int = None
    surface: str = None
    width: float = None
    bicycles_allowed: bool = None
    lit: bool = None
    layer: int = None
    foot: AccessType = None
    tunnel: str = None
    access: AccessType = None
    motor_vehicle: AccessType = None
    handrail: HandrailType = None
    vehicle: bool = None
    bicycle: AccessType = None
    ramp: bool = None
    horse: bool = None
    sac_scale: str = None
    fixme: str = None
    note: str = None
    material: str = None
    tracktype: str = None
    location: Location = None
    wheelchair: bool = None
    conveying: bool = None
    level: str = None
    mtb_scale: str = None
    mtb_scale_uphill: int = None
    bridge: bool = None
    left_handrail: bool = None
    right_handrail: bool = None
    center_handrail: bool = None
    step_condition: StepCondition = None
    tactile_paving: bool = None
    trail_visibility: TrailVisibility = None
    start_date: str = None
    covered: bool = None
    escalator: bool = None
    sidewalk: SidewalkType = None
    service: Service = None
    step_height: StepHeight = None
    step_length: StepLength = None
    motorcar: bool = None
    winter_service: bool = None
    cutting: bool = None
