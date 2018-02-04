import enum
from .enums import BarrierType, AccessType, ManMade, TrafficCalmingType, KerbType, RoadType, BridgeStructure, RailWayType, Service
from . import Named
from ..validated_quantity import quantity

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
    type: BarrierType
    foot: AccessType = None
    bicycle: AccessType = None
    vehicle: AccessType = None
    horse: bool = None
    access: AccessType = None
    entrance: str = None
    motor_vehicle: str = None
    note: str = None
    maxwidth: int = None
    fence_type: str = None
    height: quantity("meter") = None
    material: str = None
    motorcar: AccessType = None
    motorcycle: bool = None
    toll: bool = None
    operator: str = None
    toll_hgv: bool = None
    opening_hours: str = None
    bollard: BollardType = None
    destination: bool = None
    noexit: bool = None
    ticks: int = None
    man_made: ManMade = None
    description: str = None
    fixme: str = None
    two_sided: bool = None
    historic: bool = None
    complete: bool = None
    layer: int = None
    wall: WallType = None
    # Create subclass?
    stile: StileType = None
    # Subclass?
    traffic_calming: TrafficCalmingType = None
    level: int = None
    wheelchair: bool = None
    liftgate_type: LiftgateType = None
    maxheight: float = None
    wikidata: str = None
    fee: str = None
    alt_name: str = None
    kerb: KerbType = None
    disused: bool = None
    width: float = None
    leaf_type: LeafType = None
    colour: str = None
    building_colour: str = None
    wikipedia: str = None
    hgv: bool = None
    website: str = None
    count: int = None
    network: str = None
    state: BarrierType = None
    sorting_name: str = None
    abandoned_highway: RoadType = None
    bridge_structure: BridgeStructure = None
    stroller: bool = None
    pedestrians: AccessType = None
    mofa: bool = None
    ford: bool = None
    disused_railway: RailWayType = None
    service: Service = None
    goods: bool = None
    comment: str = None
    agricultural: bool = None
    swing_gate_type: SwingGateType = None