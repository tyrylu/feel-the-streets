import enum
from . import Named
from .enums import WheelchairAccess, RouteType, RouteImportance

class RouteState(enum.Enum):
    recommended = 0
    proposed = 1
    alternate = 2
    connection = 3

class RouteService(enum.Enum):
    long_distance = 0

class FerryType(enum.Enum):
    local = 0
    unclassified = 1

class Route(Named):
    type: RouteType
    complete: str = None
    destinations: str = None
    kct_red: RouteImportance = None
    network: str = None
    note: str = None
    operator: str = None
    symbol: str = None
    kct_yellow: RouteImportance = None
    kct_green: RouteImportance = None
    kct_blue: RouteImportance = None
    alt_name: str = None
    description: str = None
    from_: str = None
    kct_none: RouteImportance = None
    wikidata: str = None
    wikipedia: str = None
    to: str = None
    fixme: str = None
    distance: str = None
    state: RouteState = None
    website: str = None
    lcn_description: str = None
    colour: str = None
    service: RouteService = None
    via: str = None
    public_transport_version: int = None
    wheelchair: WheelchairAccess = None
    text_colour: str = None
    note_1: str = None
    note_2: str = None
    trail_type: RouteImportance = None
    public_transport: str = None
    designation: str = None
    short_name: str = None
    section: str = None
    icn_ref: int = None
    route_master: RouteType = None
    bicycle: bool = None
    foot: bool = None
    motor_vehicle: bool = None
    opening_hours: str = None
    duration: str = None
    fee: bool = None
    road_components: int = None
    ferry: FerryType = None
    start_date: str = None
    a: int = None
    destination: str = None
    official_name: str = None
    opening_date: str = None
    roundtrip: bool = None
    nat_ref: str = None
    kct_white: RouteImportance = None
    note_cz: str = None
