import enum
from .enums import AerialWayType, RoadType, RoofShape, BridgeStructure, AccessType, ManMade, BarrierType
from . import Named

class AerodromeType(enum.Enum):
    private = 0
    international = 1

class Subtype(enum.Enum):
    gp = 0
    loc = 1

class BeaconType(enum.Enum):
    ILS = 0

class RunwayType(enum.Enum):
    blast_pad = 0

class MilitaryRelationship(enum.Enum):
    airfield = 0

class AirMarkType(enum.Enum):
    beacon = 0

class AerialWay(Named):
    type: AerialWayType
    capacity: int = None
    occupancy: int = None
    duration: int = None
    wikipedia: str = None
    building: str = None
    length: int = None
    width: int = None
    heading: str = None
    surface: str = None
    aerodrome_type: AerodromeType = None
    icao: str = None
    roof_shape: RoofShape = None
    heating: bool = None
    pedestrian: bool = None
    highway: RoadType = None
    bridge_structure: BridgeStructure = None
    bridge: bool = None
    wikidata: str = None
    operator: str = None
    is_in: str = None
    maxweight: float = None
    description: str = None
    area: bool = None
    ele: float = None
    start_date: str = None
    height: float = None
    layer: int = None
    note: str = None
    access: AccessType = None
    lit: bool = None
    navigationaid: str = None
    man_made: ManMade = None
    frequency: str = None
    disused_aeroway: AerialWayType = None
    subtype: Subtype = None
    note_cs: str = None
    oneway: bool = None
    proposed: AerialWayType = None
    beacon_type: BeaconType = None
    runway: RunwayType = None
    barrier: BarrierType = None
    email: str = None
    phone: str = None
    military: MilitaryRelationship = None
    loc_name: str = None
    min_height: int = None
    emergency: bool = None
    building_levels: int = None
    airmark: AirMarkType = None
    iata: str = None
