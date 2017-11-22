import enum
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from .enums import CrossingType, BuildingType, RailWayType, TunnelType, BridgeType, Location, AccessType, BridgeStructure, OSMObjectType, WheelchairAccess
from . import Named

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

class SwitchType(enum.Enum):
    abt = 1
    default = 2
    double_slip = 3
    single_slip = 4
    
class SignalForm(enum.Enum):
    sign = 0
    light = 1

class SignalFunction(enum.Enum):
    block = 0
    entry = 1
    exit = 2
    intermediate = 3
class SignalHeight(enum.Enum):
    normal = 0
    dwarf = 1

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

class CrossingBarrier(enum.Enum):
    no = 0
    yes = 1
    full = 2
    half = 3
    double_half = 4
class RailWay(Named):
    __tablename__ = "rail_ways"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'rail_way'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(RailWayType), nullable=False)
    gauge = Column(UnicodeText)
    usage = Column(IntEnum(RailWayUsage))
    electrified = Column(UnicodeText)
    tracks = Column(Integer)
    maxspeed = Column(Integer)
    passenger_lines = Column(Integer)
    service = Column(UnicodeText)
    layer = Column(Integer)
    is_bridge = Column(IntEnum(BridgeType))
    tunnel = Column(IntEnum(TunnelType))
    fixme = Column(UnicodeText)
    ele = Column(Integer)
    crossing_light = Column(Boolean)
    crossing_bell = Column(Boolean)
    crossing_barrier = Column(IntEnum(CrossingBarrier))
    crossing_type = Column(IntEnum(CrossingType))
    supervised = Column(Boolean)
    surface = Column(UnicodeText)
    building_type = Column(IntEnum(BuildingType))
    flats = Column(Integer)
    levels = Column(Integer)
    oneway = Column(Boolean)
    tram_oneway = Column(Boolean)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    cutting = Column(Boolean)
    frequency = Column(Float)
    voltage = Column(Integer)
    traffic_mode = Column(UnicodeText)
    preferred_direction = Column(UnicodeText)
    wheelchair = Column(IntEnum(WheelchairAccess))
    location = Column(IntEnum(Location))
    operator = Column(UnicodeText)
    bicycle = Column(Boolean)
    horse = Column(Boolean)
    hazard = Column(IntEnum(HazardType))
    alt_name = Column(UnicodeText)
    old_name = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    image = Column(UnicodeText) # Some Column(URL) would be more appropriate
    network = Column(UnicodeText)
    etcs = Column(UnicodeText)
    radio = Column(UnicodeText)
    track_class = Column(IntEnum(TrackClass))
    tilting_maxspeed = Column(Integer)
    structure_gauge = Column(IntEnum(StructureGauge))
    bidirectional = Column(IntEnum(Bidirectionality))
    ls = Column(Boolean)
    track_ref = Column(UnicodeText)
    note = Column(UnicodeText)
    start_date = Column(UnicodeText)
    covered = Column(Boolean)
    description = Column(UnicodeText)
    embankment = Column(Boolean)
    proposed = Column(IntEnum(RailWayType))
    access = Column(IntEnum(AccessType))
    maxheight = Column(Float)
    disused = Column(IntEnum(RailWayType))
    abandoned_railway = Column(IntEnum(RailWayType))
    end_date = Column(UnicodeText)
    bridge_name = Column(UnicodeText)
    comment = Column(UnicodeText)
    colour = Column(IntEnum(Colour))
    station = Column(IntEnum(RailWayType))
    transport = Column(IntEnum(RailWayType))
    level = Column(Integer)
    construction = Column(IntEnum(RailWayType))
    foot = Column(Boolean)
    train = Column(Boolean)
    switch = Column(IntEnum(SwitchType))
    bridge_structure = Column(IntEnum(BridgeStructure))
    disused_railway = Column(IntEnum(RailWayType))
    loc_name = Column(UnicodeText)
    shelter = Column(Boolean)
    check_date = Column(UnicodeText) # Find a way how to parse the dates nicely
    pzb = Column(Boolean)
    tunnel_name = Column(UnicodeText)
    height = Column(Float)
    length = Column(Float)
    indoor_level = Column(UnicodeText)
    highspeed = Column(Boolean)
    gnt = Column(Boolean)
    lzb = Column(Boolean)
    tilting = Column(Boolean)
    traces = Column(Integer)
    forward_maxspeed = Column(Integer)
    backward_maxspeed = Column(Integer)
    main_switch_off = Column(Boolean)
    exact_position = Column(Float)
    local_operated = Column(Boolean)
    signal_direction = Column(IntEnum(SignalDirection))
    signal_position = Column(IntEnum(SignalPosition))
    shunting_signal = Column(UnicodeText)
    shunting_signal_form = Column(IntEnum(SignalForm))
    shunting_signal_height = Column(IntEnum(SignalHeight))
    shunting_signal_states = Column(UnicodeText)
    main_repeated_signal = Column(UnicodeText)
    main_repeated_signal_form = Column(IntEnum(SignalForm))
    main_repeated_signal_states = Column(UnicodeText)
    distant_signal = Column(UnicodeText)
    distant_signal_form = Column(IntEnum(SignalForm))
    distant_signal_height = Column(IntEnum(SignalHeight))
    distant_signal_states = Column(UnicodeText)
    main_signal = Column(UnicodeText)
    main_signal_form = Column(IntEnum(SignalForm))
    main_signal_function = Column(IntEnum(SignalFunction))
    main_signal_height = Column(IntEnum(SignalHeight))
    main_signal_states = Column(UnicodeText)
    main_signal_substitute_signal = Column(UnicodeText)
    distant_speed_limit_signal = Column(UnicodeText)
    distant_speed_limit_signal_form = Column(IntEnum(SignalForm))
    distant_speed_limit_signal_height = Column(IntEnum(SignalHeight))
    distant_speed_limit_signal_speed = Column(Integer)
    electricity_signal = Column(UnicodeText)
    electricity_signal_form = Column(IntEnum(SignalForm))
    electricity_signal_height = Column(IntEnum(SignalHeight))
    electricity_signal_type = Column(IntEnum(ElectricitySignal))
    speed_limit_signal = Column(UnicodeText)
    speed_limit_signal_form = Column(IntEnum(SignalForm))
    speed_limit_signal_height = Column(IntEnum(SignalHeight))
    speed_limit_signal_speed = Column(UnicodeText)
    crossing_activation = Column(IntEnum(CrossingActivation))
    crossing_saltire = Column(Boolean)
    position = Column(Float)
    distant_signal_deactivated = Column(Boolean)
    main_signal_deactivated = Column(Boolean)
    shunting_signal_deactivated = Column(Boolean)
    main_repeated_signal_deactivated = Column(Boolean)
    distant_station_signal = Column(UnicodeText)
    distant_station_signal_form = Column(IntEnum(SignalForm))
    snowplow_signal = Column(UnicodeText)
    snowplow_signal_form = Column(IntEnum(SignalForm))
    snowplow_signal_type = Column(IntEnum(SignalType))
    diverging_maxspeed = Column(Integer)
    straight_maxspeed = Column(Integer)
    distant_crossing_signal = Column(UnicodeText)
    distant_crossing_signal_form = Column(IntEnum(SignalForm))
    main_repeated_signal_substitute_signal = Column(UnicodeText)
    distant_crossing_signal_deactivated = Column(Boolean)
    turnout_side = Column(IntEnum(TurnoutSide))
    distant_crossing_signal_caption = Column(UnicodeText)
    snowplow_signal_deactivated = Column(Boolean)
    minor_signal = Column(UnicodeText)
    minor_signal_form = Column(IntEnum(SignalForm))
    minor_signal_deactivated = Column(Boolean)
    minor_signal_height = Column(IntEnum(SignalHeight))
    minor_signal_states = Column(UnicodeText)
    electric_switch = Column(Boolean)
    minor_signal_substitute_signal = Column(UnicodeText)
    speed_limit_signal_deactivated = Column(Boolean)
    electricity_signal_deactivated = Column(Boolean)
    distant_station_signal_deactivated = Column(Boolean)
    left_avalanche_protector = Column(IntEnum(AvalancheProtectorType))
    reg_name = Column(UnicodeText)
    area = Column(Boolean)
    catenary_mast_milestone = Column(Boolean)
    emergency_brake_override_milestone = Column(Boolean)
    hot_box_defect_detector = Column(Boolean)