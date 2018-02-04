import enum
from .enums import CrossingType, BuildingType, RailWayType, TunnelType, BridgeType, Location, AccessType, BridgeStructure, WheelchairAccess, EntranceType, BarrierType
from . import Named, Address

class AvalancheProtectorType(enum.Enum):
    open = 0
    
class RailWayUsage(enum.Enum):
    unknown = 0
    main = 1
    branch = 2
    industrial = 3
    tourism = 4
    
class HazardType(enum.Enum):
    dangerous_junction = 1

class TrackClass(enum.Enum):
    C3 = 1
    D4 = 2
    D3 = 3
    
class SignalPosition(enum.Enum):
    left = 0
    right = 1
    overhead = 2
    bridge = 3
    above = 4

class StructureGauge(enum.Enum):
    GC = 1

class Bidirectionality(enum.Enum):
    regular = 1

class SignalDirection(enum.Enum):
    backward = 0
    forward = 1

class Colour(enum.Enum):
    green = 1
    red = 2
    yellow = 3

class SwitchType(enum.Enum):
    abt = 1
    default = 2
    double_slip = 3
    single_slip = 4
    
class SignalForm(enum.Enum):
    sign = 0
    light = 1
    semaphore = 2

class SignalFunction(enum.Enum):
    block = 0
    entry = 1
    exit = 2
    intermediate = 3
    between = 4

class SignalHeight(enum.Enum):
    normal = 0
    dwarf = 1
    main = 2

class SignalType(enum.Enum):
    down = 0
    up = 1

class CrossingActivation(enum.Enum):
    automatic = 0
    remote = 1
    local = 2

class TurnoutSide(enum.Enum):
    left = 0
    right = 1

class ElectricitySignal(enum.Enum):
    power_on = 0
    pantograph_up = 1
    pantograph_down = 2
    power_off = 3
    power_off_advance = 4
    end_of_catenary = 5

class CrossingBarrier(enum.Enum):
    no = 0
    yes = 1
    full = 2
    half = 3
    double_half = 4
    lift_gate = 5
    both = 6

class SwitchConfiguration(enum.Enum):
    inside = 0

class RailWay(Named):
    type: RailWayType
    gauge: str = None
    usage: RailWayUsage = None
    electrified: str = None
    tracks: int = None
    maxspeed: int = None
    passenger_lines: int = None
    service: str = None
    layer: int = None
    is_bridge: BridgeType = None
    tunnel: TunnelType = None
    fixme: str = None
    ele: int = None
    crossing_light: bool = None
    crossing_bell: bool = None
    crossing_barrier: CrossingBarrier = None
    crossing_type: CrossingType = None
    supervised: bool = None
    surface: str = None
    building_type: BuildingType = None
    flats: int = None
    levels: int = None
    oneway: bool = None
    tram_oneway: bool = None
    address: Address = None
    cutting: bool = None
    frequency: float = None
    voltage: int = None
    traffic_mode: str = None
    preferred_direction: str = None
    wheelchair: WheelchairAccess = None
    location: Location = None
    operator: str = None
    bicycle: bool = None
    horse: bool = None
    hazard: HazardType = None
    alt_name: str = None
    old_name: str = None
    wikidata: str = None
    wikipedia: str = None
    image: str = None
    network: str = None
    etcs: str = None
    radio: str = None
    track_class: TrackClass = None
    tilting_maxspeed: int = None
    structure_gauge: StructureGauge = None
    bidirectional: Bidirectionality = None
    ls: bool = None
    track_ref: str = None
    note: str = None
    start_date: str = None
    covered: bool = None
    description: str = None
    embankment: bool = None
    proposed: RailWayType = None
    access: AccessType = None
    maxheight: float = None
    disused: RailWayType = None
    abandoned_railway: RailWayType = None
    end_date: str = None
    bridge_name: str = None
    comment: str = None
    colour: Colour = None
    station: RailWayType = None
    transport: RailWayType = None
    level: int = None
    construction: RailWayType = None
    foot: bool = None
    train: bool = None
    switch: SwitchType = None
    bridge_structure: BridgeStructure = None
    disused_railway: RailWayType = None
    loc_name: str = None
    shelter: bool = None
    check_date: str = None
    # Find a way how to parse the dates nicely
    pzb: bool = None
    tunnel_name: str = None
    height: float = None
    length: float = None
    indoor_level: str = None
    highspeed: bool = None
    gnt: bool = None
    lzb: bool = None
    tilting: bool = None
    traces: int = None
    forward_maxspeed: int = None
    backward_maxspeed: int = None
    main_switch_off: bool = None
    exact_position: float = None
    local_operated: bool = None
    signal_direction: SignalDirection = None
    signal_position: SignalPosition = None
    shunting_signal: str = None
    shunting_signal_form: SignalForm = None
    shunting_signal_height: SignalHeight = None
    shunting_signal_states: str = None
    main_repeated_signal: str = None
    main_repeated_signal_form: SignalForm = None
    main_repeated_signal_states: str = None
    distant_signal: str = None
    distant_signal_form: SignalForm = None
    distant_signal_height: SignalHeight = None
    distant_signal_states: str = None
    main_signal: str = None
    main_signal_form: SignalForm = None
    main_signal_function: SignalFunction = None
    main_signal_height: SignalHeight = None
    main_signal_states: str = None
    main_signal_substitute_signal: str = None
    distant_speed_limit_signal: str = None
    distant_speed_limit_signal_form: SignalForm = None
    distant_speed_limit_signal_height: SignalHeight = None
    distant_speed_limit_signal_speed: int = None
    electricity_signal: str = None
    electricity_signal_form: SignalForm = None
    electricity_signal_height: SignalHeight = None
    electricity_signal_type: ElectricitySignal = None
    speed_limit_signal: str = None
    speed_limit_signal_form: SignalForm = None
    speed_limit_signal_height: SignalHeight = None
    speed_limit_signal_speed: str = None
    crossing_activation: CrossingActivation = None
    crossing_saltire: bool = None
    position: float = None
    distant_signal_deactivated: bool = None
    main_signal_deactivated: bool = None
    shunting_signal_deactivated: bool = None
    main_repeated_signal_deactivated: bool = None
    distant_station_signal: str = None
    distant_station_signal_form: SignalForm = None
    snowplow_signal: str = None
    snowplow_signal_form: SignalForm = None
    snowplow_signal_type: SignalType = None
    diverging_maxspeed: int = None
    straight_maxspeed: int = None
    distant_crossing_signal: str = None
    distant_crossing_signal_form: SignalForm = None
    main_repeated_signal_substitute_signal: str = None
    distant_crossing_signal_deactivated: bool = None
    turnout_side: TurnoutSide = None
    distant_crossing_signal_caption: str = None
    snowplow_signal_deactivated: bool = None
    minor_signal: str = None
    minor_signal_form: SignalForm = None
    minor_signal_deactivated: bool = None
    minor_signal_height: SignalHeight = None
    minor_signal_states: str = None
    electric_switch: bool = None
    minor_signal_substitute_signal: str = None
    speed_limit_signal_deactivated: bool = None
    electricity_signal_deactivated: bool = None
    distant_station_signal_deactivated: bool = None
    left_avalanche_protector: AvalancheProtectorType = None
    reg_name: str = None
    area: bool = None
    catenary_mast_milestone: bool = None
    emergency_brake_override_milestone: bool = None
    hot_box_defect_detector: bool = None
    network_en: str = None
    speed_limit_signal_deactivatedd: bool = None
    tram: bool = None
    entrance: EntranceType = None
    abandoned: RailWayType = None
    switch_configuration: SwitchConfiguration = None
    crossing_on_demand: bool = None
    distant_signal_repeated: bool = None
    workrules: str = None
    switch_resetting: bool = None
    wheelchair_toilets: bool = None
    barrier: BarrierType = None
    combined_signal: str = None
    combined_signal_function: SignalFunction = None
    wrong_road_signal: str = None
    electricity_signal_turn_direction: str = None
    oneway_1: bool = None
    website: str = None
    historic: bool = None
    combined_signal_states: str = None
    route_signal: str = None
    route_signal_states: str = None
    todo: str = None
    is_in: str = None
    platforms: int = None