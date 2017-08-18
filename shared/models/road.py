import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Float, Integer, UnicodeText
from geoalchemy import GeometryColumn, LineString
import shapely.wkt as wkt
from .enums import AccessType, WaterWayType, NaturalType, Inclination, CrossingType, TrafficCalmingType, RailWayType, BridgeType, RoadType, Location
from . import Named

class JunctionType(enum.Enum):
    none = 0
    roundabout = 1

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

class FootwayType(enum.Enum):
    unknown = 0
    sidewalk = 1
    crossing = 2

class HGVAccessType(enum.Enum):
    unspecified = 0
    destination = 1
    no = 2

class FootType(enum.Enum):
    no = 0
    yes = 1
    designated = 2
    private = 3

class DestinationSymbol(enum.Enum):
    industrial = 1

class Symbol(enum.Enum):
    stadium = 0
class Road(Named):
    __tablename__ = "roads"
    __mapper_args__ = {'polymorphic_identity': 'road'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    original_geometry = GeometryColumn(LineString(2))
    type = Column(Enum(RoadType))
    railway = Column(Enum(RailWayType))
    int_ref = Column(UnicodeText)
    maxspeed = Column(Integer)
    maxspeed_hgv = Column(Integer)
    maxspeed_forward = Column(Integer)
    maxspeed_backward = Column(Integer)
    hgv = Column(Enum(HGVAccessType))
    lanes = Column(Integer)
    oneway = Column(Boolean)
    tram_oneway = Column(Boolean)
    bicycle_oneway = Column(Boolean)
    junction_type = Column(Enum(JunctionType))
    bridge = Column(Enum(BridgeType))
    bridge_structure = Column(UnicodeText)
    layer = Column(Integer)
    sidewalk = Column(Enum(SidewalkType))
    note = Column(UnicodeText)
    foot = Column(Enum(AccessType))
    bicycle_allowed = Column(Enum(AccessType))
    motor_vehicle_allowed = Column(Enum(AccessType))
    motorcycle_allowed = Column(Boolean)
    vehicle_allowed = Column(Enum(AccessType))
    maxheight = Column(Float)
    segregated = Column(Boolean)
    tracktype = Column(UnicodeText)
    maxweight = Column(Float)
    access = Column(Enum(AccessType))
    surface = Column(UnicodeText)
    width = Column(Float)
    smoothness = Column(UnicodeText)
    cycleway = Column(Enum(CycleWayType))
    right_cycleway = Column(Enum(CycleWayType))
    left_cycleway = Column(Enum(CycleWayType))
    backward_lanes = Column(Integer)
    forward_lanes = Column(Integer)
    tunnel = Column(UnicodeText)
    footway_type = Column(Enum(FootwayType))
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
    waterway = Column(Enum(WaterWayType))
    dogs_allowed = Column(Boolean)
    goods = Column(Boolean)
    natural = Column(Enum(NaturalType))
    service = Column(UnicodeText)
    pedestrian = Column(Boolean)
    wheelchair = Column(Boolean)
    proposed = Column(Enum(RoadType))
    noname = Column(Boolean)
    gauge = Column(UnicodeText)
    tracks = Column(Integer)
    cutting = Column(Boolean)
    incline = Column(Enum(Inclination))
    handrail = Column(Boolean)
    end_date = Column(UnicodeText)
    maxaxleload = Column(Float)
    psv = Column(Boolean)
    crossing = Column(Enum(CrossingType))
    sac_scale = Column(UnicodeText)
    trail_visibility = Column(UnicodeText)
    covered = Column(UnicodeText)
    ford = Column(Boolean)
    traffic_calming = Column(Enum(TrafficCalmingType))
    roller_ski = Column(Enum(AccessType))
    destination = Column(UnicodeText)
    colour = Column(UnicodeText)
    destination_symbol = Column(Enum(DestinationSymbol))
    symbol = Column(Enum(Symbol))
    kct_blue = Column(Boolean)
    name_1 = Column(UnicodeText)
    location = Column(Enum(Location))
    lane_destinations = Column(UnicodeText)
    
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
