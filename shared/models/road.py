import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from geoalchemy import GeometryColumn, LineString
import shapely.wkt as wkt
from .enums import AccessType, WaterWayType, NaturalType, Inclination, CrossingType, TrafficCalmingType, RailWayType, BridgeType, RoadType, Location, BridgeStructure, OSMObjectType
from . import Named

class JunctionType(enum.Enum):
    none = 0
    roundabout = 1
    circular = 2
    
class SidewalkType(enum.Enum):
    unknown = 0
    left = 1
    right = 2
    both = 3
    no = 4
    separate = 5
    none = 6

class CycleWayType(enum.Enum):
    none = 0
    opposite_lane = 1
    lane = 2
    opposite = 3
    track = 4
    no = 5
    crossing = 6
    share_busway = 7
    shared_lane = 8
    opposite_track = 9
    yes = 10
    
    
class FootwayType(enum.Enum):
    unknown = 0
    sidewalk = 1
    crossing = 2
    separate = 3
    yes = 4
    right = 5
    
    
class HGVAccessType(enum.Enum):
    unspecified = 0
    destination = 1
    no = 2
    delivery = 3

class FootType(enum.Enum):
    no = 0
    yes = 1
    designated = 2
    private = 3

class DestinationSymbol(enum.Enum):
    industrial = 1
    airport = 2
    hospital = 3
    motorway = 4
    fuel = 5
    shopping = 6
    motorroad = 7
    

class Symbol(enum.Enum):
    stadium = 0

class AbuttersType(enum.Enum):
    residential = 0

class Road(Named):
    __tablename__ = "roads"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'road'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    original_geometry = GeometryColumn(LineString(2))
    type = Column(IntEnum(RoadType))
    railway = Column(IntEnum(RailWayType))
    int_ref = Column(UnicodeText)
    maxspeed = Column(Integer)
    maxspeed_hgv = Column(Integer)
    maxspeed_forward = Column(Integer)
    maxspeed_backward = Column(Integer)
    hgv = Column(IntEnum(AccessType))
    lanes = Column(Integer)
    oneway = Column(Boolean)
    tram_oneway = Column(Boolean)
    bicycle_oneway = Column(Boolean)
    junction_type = Column(IntEnum(JunctionType))
    bridge = Column(IntEnum(BridgeType))
    bridge_structure = Column(IntEnum(BridgeStructure))
    layer = Column(Integer)
    sidewalk = Column(IntEnum(SidewalkType))
    note = Column(UnicodeText)
    foot = Column(IntEnum(AccessType))
    bicycle_allowed = Column(IntEnum(AccessType))
    motor_vehicle_allowed = Column(IntEnum(AccessType))
    motorcycle_allowed = Column(Boolean)
    vehicle_allowed = Column(IntEnum(AccessType))
    maxheight = Column(Float)
    segregated = Column(Boolean)
    tracktype = Column(UnicodeText)
    maxweight = Column(Float)
    access = Column(IntEnum(AccessType))
    surface = Column(UnicodeText)
    width = Column(Float)
    smoothness = Column(UnicodeText)
    cycleway = Column(IntEnum(CycleWayType))
    right_cycleway = Column(IntEnum(CycleWayType))
    left_cycleway = Column(IntEnum(CycleWayType))
    backward_lanes = Column(Integer)
    forward_lanes = Column(Integer)
    tunnel = Column(UnicodeText)
    footway_type = Column(IntEnum(FootwayType))
    inline_skates_allowed = Column(Boolean)
    exit_to = Column(UnicodeText)
    lit = Column(Boolean)
    alt_name = Column(UnicodeText)
    fixme = Column(UnicodeText)
    toll = Column(Boolean)
    maxlength = Column(Integer)
    opening_date = Column(UnicodeText)
    route = Column(UnicodeText)
    noexit = Column(Boolean)
    horse_allowed = Column(Boolean)
    comment = Column(UnicodeText)
    waterway = Column(IntEnum(WaterWayType))
    dogs_allowed = Column(Boolean)
    goods = Column(Boolean)
    natural = Column(IntEnum(NaturalType))
    service = Column(UnicodeText)
    pedestrian = Column(Boolean)
    wheelchair = Column(Boolean)
    proposed = Column(IntEnum(RoadType))
    noname = Column(Boolean)
    gauge = Column(UnicodeText)
    tracks = Column(Integer)
    cutting = Column(Boolean)
    incline = Column(IntEnum(Inclination))
    handrail = Column(Boolean)
    end_date = Column(UnicodeText)
    maxaxleload = Column(Float)
    psv = Column(Boolean)
    crossing = Column(IntEnum(CrossingType))
    sac_scale = Column(UnicodeText)
    trail_visibility = Column(UnicodeText)
    covered = Column(UnicodeText)
    ford = Column(Boolean)
    traffic_calming = Column(IntEnum(TrafficCalmingType))
    roller_ski = Column(IntEnum(AccessType))
    destination = Column(UnicodeText)
    colour = Column(UnicodeText)
    destination_symbol = Column(IntEnum(DestinationSymbol))
    symbol = Column(IntEnum(Symbol))
    kct_blue = Column(Boolean)
    name_1 = Column(UnicodeText)
    location = Column(IntEnum(Location))
    lane_destinations = Column(UnicodeText)
    trolley_wire = Column(Boolean)
    proposed_bridge = Column(Boolean)
    abutters = Column(IntEnum(AbuttersType))
    embankment = Column(Boolean)
    
    
    @property
    def effective_width(self):
        if self.width:
            return self.width
        else:
            if self.lanes:
                lanes = self.lanes
            else:
                lanes = 1
            return 2 * lanes

    def get_original_shapely_geometry(self, db):
        return wkt.loads(db.scalar(self.original_geometry.wkt()))