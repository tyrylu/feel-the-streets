import enum
from . import Named
from .enums import WheelchairAccess, ConstructionType, Direction, ShelterType

class Transport(enum.Enum):
    subway = 0

class StationType(enum.Enum):
    subway = 0

class StopType(enum.Enum):
    must_infer = -1
    bus_stop = 0
    bus_station = 1
    tram_stop = 2
    stop = 3
    station = 4
    survey = 5
    disused = 6
    construction = 7
    stop_area = 8
    facility = 9
    public_transport = 10
    halt = 11
    
class Stop(Named):
    type: StopType = None
    bus: bool = None
    tram: bool = None
    train: bool = None
    old_name: str = None
    has_shelter: bool = None
    covered: bool = None
    bench: bool = None
    operator: str = None
    tactile_paving: bool = None
    opening_hours: str = None
    network: str = None
    layer: int = None
    building: bool = None
    area: bool = None
    zone: int = None
    wheelchair: WheelchairAccess = None
    note: str = None
    trolleybus: bool = None
    alt_name: str = None
    route_ref: str = None
    # More exactly it is an array of ints...
    local_ref: str = None
    fixme: str = None
    ele: float = None
    image: str = None
    wikidata: str = None
    wikipedia: str = None
    ref_name: str = None
    short_name: str = None
    bin: bool = None
    official_name: str = None
    comment: str = None
    complete: bool = None
    disused: bool = None
    uic_name: str = None
    uic_ref: int = None
    direction: Direction = None
    alt_name_de: str = None
    old_name_de: str = None
    website: str = None
    colour: str = None
    network_en: str = None
    station: StationType = None
    subway: bool = None
    transport: Transport = None
    network_cs: str = None
    start_date: str = None
    description: str = None
    rail: bool = None
    level: int = None
    construction: ConstructionType = None
    access: bool = None
    wheelchair_toilets: bool = None
    lines: str = None
    destination: str = None
    check_date: str = None
    oneway: bool = None
    shelter_type: ShelterType = None
