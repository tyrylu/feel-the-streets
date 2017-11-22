import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum, DimensionalFloat
from geoalchemy import GeometryColumn, LineString
import shapely.wkt as wkt
from .enums import AccessType, WaterWayType, NaturalType, Inclination, CrossingType, TrafficCalmingType, RailWayType, BridgeType, RoadType, Location, BridgeStructure, OSMObjectType, Surface, KerbType, SidewalkType, WheelchairAccess, ManMade, HistoricType, RestrictionType, SportType
from . import Named

class JunctionType(enum.Enum):
    none = 0
    roundabout = 1
    circular = 2
    
class SpeedVariable(enum.Enum):
    obstruction = 0

class TactilePaving(enum.Enum):
    no = 0
    yes = 1
    incorrect = 2
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
    segregated = 11

class CutlineType(enum.Enum):
        pipeline = 0
    
class MaxspeedType(enum.Enum):
    sign = 0
    
class ParkingCondition(enum.Enum):
        free = 0
    
class BuswayLaneType(enum.Enum):
    lane = 0
class FootwayType(enum.Enum):
    unknown = 0
    sidewalk = 1
    crossing = 2
    separate = 3
    yes = 4
    right = 5
    left = 6
    

class RoadPriority(enum.Enum):
    designated = 0

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
    centre = 8
    
    

class Busway(enum.Enum):
    lane = 0
class Symbol(enum.Enum):
    stadium = 0

class AbuttersType(enum.Enum):
    residential = 0
class ParkingLaneType(enum.Enum):
    no_parking = 0
    diagonal = 1
    no_stopping = 2
    parallel = 3
    perpendicular = 4
    inline = 5
    marked = 6
    on_street = 7

class Cutting(enum.Enum):
    no = 0
    yes = 1
    right = 2
class RampType(enum.Enum):
    yes = 0
    up = 1

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
    lanes = Column(Float)
    oneway = Column(UnicodeText)
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
    motorcycle_allowed = Column(IntEnum(AccessType))
    vehicle_allowed = Column(IntEnum(AccessType))
    horse_allowed = Column(IntEnum(AccessType))
    maxheight = Column(Float)
    segregated = Column(Boolean)
    tracktype = Column(UnicodeText)
    maxweight = Column(Float)
    access = Column(IntEnum(AccessType))
    surface = Column(IntEnum(Surface))
    width = Column(DimensionalFloat("meter"))
    smoothness = Column(UnicodeText)
    cycleway = Column(IntEnum(CycleWayType))
    right_cycleway = Column(IntEnum(CycleWayType))
    left_cycleway = Column(IntEnum(CycleWayType))
    backward_lanes = Column(Integer)
    forward_lanes = Column(Integer)
    tunnel = Column(UnicodeText)
    footway_type = Column(IntEnum(FootwayType))
    inline_skates_allowed = Column(IntEnum(AccessType))
    exit_to = Column(UnicodeText)
    lit = Column(Boolean)
    alt_name = Column(UnicodeText)
    fixme = Column(UnicodeText)
    toll = Column(Boolean)
    maxlength = Column(Integer)
    opening_date = Column(UnicodeText)
    route = Column(UnicodeText)
    noexit = Column(Boolean)
    maxspeed = Column(Integer)
    owed = Column(IntEnum(AccessType))
    comment = Column(UnicodeText)
    waterway = Column(IntEnum(WaterWayType))
    dogs_allowed = Column(Boolean)
    goods = Column(IntEnum(AccessType))
    natural = Column(IntEnum(NaturalType))
    service = Column(UnicodeText)
    pedestrian = Column(Boolean)
    wheelchair = Column(IntEnum(WheelchairAccess))
    proposed = Column(IntEnum(RoadType))
    noname = Column(Boolean)
    gauge = Column(UnicodeText)
    tracks = Column(Integer)
    cutting = Column(IntEnum(Cutting))
    incline = Column(IntEnum(Inclination))
    handrail = Column(Boolean)
    end_date = Column(UnicodeText)
    maxaxleload = Column(Float)
    psv = Column(IntEnum(AccessType))
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
    railway_lanes_backward = Column(UnicodeText)
    railway_lanes_forward = Column(UnicodeText)
    ticks = Column(Float)
    change_lanes_backward = Column(UnicodeText)
    change_lanes_forward = Column(UnicodeText)
    psv_lanes_backward = Column(UnicodeText)
    psv_lanes_forward = Column(UnicodeText)
    parking_lane_left = Column(IntEnum(ParkingLaneType))
    parking_lane_both = Column(IntEnum(ParkingLaneType))
    parking_lane_right = Column(IntEnum(ParkingLaneType))
    bus_lanes_backward = Column(UnicodeText)
    bus_lanes_forward = Column(UnicodeText)
    busway = Column(IntEnum(Busway))
    vehicle_lanes_backward = Column(UnicodeText)
    vehicle_lanes_forward = Column(UnicodeText)
    railway_lanes = Column(UnicodeText)
    busway_right = Column(IntEnum(BuswayLaneType))
    old_name = Column(UnicodeText)
    destination_lanes_colours = Column(UnicodeText)
    forward_destination = Column(UnicodeText)
    start_date = Column(UnicodeText)
    motorcar = Column(IntEnum(AccessType))
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    tube = Column(Boolean)
    description = Column(UnicodeText)
    material = Column(IntEnum(Surface))
    change_lanes = Column(UnicodeText)
    traffic_zone = Column(UnicodeText)
    maxwidth = Column(Float)
    mtb_bicycle_class = Column(Integer)
    backward_destination = Column(UnicodeText)
    snowplowing = Column(Boolean)
    winter_service = Column(Boolean)
    technical_mtb_bicycle_class = Column(Integer)
    narrow = Column(Boolean)
    opening_hours = Column(UnicodeText)
    man_made = Column(IntEnum(ManMade))
    operator = Column(UnicodeText)
    kerb = Column(IntEnum(KerbType))
    tactile_paving = Column(IntEnum(TactilePaving))
    complete = Column(Boolean)
    est_width = Column(Float)
    snowmobile = Column(Boolean)
    level = Column(Integer)
    abandoned = Column(Boolean)
    ref_name = Column(UnicodeText)
    ref_name_note = Column(UnicodeText)
    placement = Column(UnicodeText)
    is_in = Column(UnicodeText)
    agricultural = Column(Boolean)
    carriage = Column(Boolean)
    lanes_maxwidth = Column(Float)
    priority_road = Column(IntEnum(RoadPriority))
    lcn = Column(Boolean)
    overtaking = Column(Boolean)
    bus = Column(Boolean)
    pl_highway_class = Column(UnicodeText)
    pl_highway_category = Column(Integer)
    bus_maxspeed = Column(Integer)
    trailer_maxspeed = Column(Integer)
    carriageway_width = Column(Float)
    wet_maxspeed = Column(Integer)
    bridge_name = Column(UnicodeText)
    variable_maxspeed = Column(IntEnum(SpeedVariable))
    sorting_name = Column(UnicodeText)
    historic = Column(IntEnum(HistoricType))
    bus_overtaking = Column(Boolean)
    hgv_overtaking = Column(Boolean)
    trailer_overtaking = Column(Boolean)
    minspeed = Column(Integer)
    ncn = Column(Boolean)
    destination_sign = Column(UnicodeText)
    area = Column(Boolean)
    short_name = Column(UnicodeText)
    hgv_6_5t = Column(Boolean)
    destination_int_ref_lanes = Column(UnicodeText)
    destination_ref_lanes = Column(UnicodeText)
    destination_symbol_lanes = Column(UnicodeText)
    left_parking_condition = Column(IntEnum(ParkingCondition))
    right_parking_condition = Column(IntEnum(ParkingCondition))
    parking_lane_both_parallel = Column(IntEnum(ParkingLaneType))
    destination_int_ref = Column(UnicodeText)
    destination_ref = Column(UnicodeText)
    maxspeed_type = Column(IntEnum(MaxspeedType))
    motor_vehicle_conditional = Column(UnicodeText)
    motor_vehicle_forward_conditional = Column(UnicodeText)
    cutline = Column(IntEnum(CutlineType))
    hgv_hour_off = Column(UnicodeText)
    hgv_hour_on = Column(UnicodeText)
    int_name = Column(UnicodeText)
    parking_lane_left_diagonal = Column(IntEnum(ParkingLaneType))
    maxspeed_conditional = Column(UnicodeText)
    forward_maxspeed_conditional = Column(UnicodeText)
    crossing_ref = Column(UnicodeText)
    motor_vehicle_backward = Column(IntEnum(AccessType))
    vehicle_forward = Column(IntEnum(AccessType))
    both_sidewalk_kerb = Column(IntEnum(KerbType))
    parking_lane_left_parallel = Column(IntEnum(ParkingLaneType))
    leaf_type = Column(UnicodeText) # Find out what they're doing there
    vehicle_forward_conditional = Column(UnicodeText)
    transit_lanes = Column(UnicodeText)
    bicycle_forward_lanes = Column(UnicodeText)
    restriction = Column(IntEnum(RestrictionType))
    wheelchair_ramp = Column(Boolean)
    hide = Column(Boolean)
    forward_maxheight = Column(Float)
    technical_bicycle_class = Column(Integer)
    ramp = Column(IntEnum(RampType))
    survey_date = Column(UnicodeText) # Make it a date
    abandoned_higway = Column(IntEnum(RoadType))
    indoor = Column(Boolean)
    informal = Column(Boolean)
    ref_name_note = Column(UnicodeText)
    ref_name = Column(UnicodeText)
    hgv_6t = Column(IntEnum(AccessType))
    old_ref = Column(Integer)
    bridge_ref = Column(UnicodeText)
    hgv_conditional_maxspeed = Column(UnicodeText)
    lane_marking = Column(Boolean)
    turn = Column(UnicodeText)
    destination_country = Column(UnicodeText)
    dual_carriageway = Column(Boolean)
    access_note = Column(UnicodeText)
    nat_ref = Column(Integer)
    left_footway_width = Column(Float)
    hazmat_water = Column(Boolean)
    hgv_12t = Column(IntEnum(AccessType))
    passing_places = Column(Boolean)
    sport = Column(IntEnum(SportType))
    hgv_3_5t = Column(IntEnum(AccessType))
    maxweight_note = Column(UnicodeText)
    alt_name_de = Column(UnicodeText)
    alt_name_en = Column(UnicodeText)
    rcn = Column(Boolean)
    rcn_ref = Column(Integer)
    distance = Column(Integer)
    
    
    
    @property
    def effective_width(self):
        if self.width:
            return self.width.magnitude
        elif self.est_width:
            return self.est_width
        elif self.carriageway_width:
            return self.carriageway_width
        else:
            if self.lanes:
                lanes = self.lanes
            else:
                lanes = 1
            if self.lanes_maxwidth:
                width = self.lanes_maxwidth
            else:
                width = 2
            return width * lanes

    def get_original_shapely_geometry(self, db):
        return wkt.loads(db.scalar(self.original_geometry.wkt()))