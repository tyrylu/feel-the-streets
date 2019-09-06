import enum
from shared.humanization_utils import underscored_to_words
from .enums import AccessType, WaterWayType, NaturalType, Inclination, CrossingType, TrafficCalmingType, RailWayType, BridgeType, RoadType, Location, BridgeStructure, Surface, KerbType, SidewalkType, WheelchairAccess, ManMade, HistoricType, RestrictionType, SportType, AreaType, TourismType, Amenity, PlaceType, RouteImportance, EmergencyType, Support, BarrierType, CurbType, BuildingType, TrafficSignType, ParkingLaneType, IndoorType
from . import Named
from ..validated_quantity import quantity

class ParkingCondition(enum.Enum):
    residents = 0
    ticket = 1
    free = 2

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
    soft_lane = 12
    oposite_track = 13

class CutlineType(enum.Enum):
        pipeline = 0
    
class MaxspeedType(enum.Enum):
    sign = 0
    zone = 1

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
    o = 7

class RoadPriority(enum.Enum):
    designated = 0
    backward = 1
    forward = 2
    end = 3

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

class Cutting(enum.Enum):
    no = 0
    yes = 1
    right = 2
    left = 3

class RampType(enum.Enum):
    yes = 0
    up = 1

class ShoulderType(enum.Enum):
    no = 0
    right = 1
    yes = 2

class Hazard(enum.Enum):
    pedestrians = 0
    traffic_signals = 1
    wild_animals = 2
    curves = 3
    side_winds = 4
    rock_slide = 5
    slippery_road = 6
    wild_animal = 7

class Divider(enum.Enum):
    line = 0

class ODBL(enum.Enum):
    clean = 0

class ArcadeType(enum.Enum):
    open = 0

class TMC_CID_58_TABCD_1_Class(enum.Enum):
    Point = 0

class Conveying(enum.Enum):
    forward = 0
    backward = 1
    reversible = 2
    yes = 3

class Stairwell(enum.Enum):
    stair_landing = 0

class Road(Named):
    type: RoadType = None
    railway: RailWayType = None
    int_ref: str = None
    maxspeed: int = None
    maxspeed_hgv: int = None
    maxspeed_forward: int = None
    maxspeed_backward: int = None
    hgv: AccessType = None
    lanes: float = None
    oneway: str = None
    tram_oneway: bool = None
    bicycle_oneway: bool = None
    junction_type: JunctionType = None
    bridge: BridgeType = None
    bridge_structure: BridgeStructure = None
    layer: int = None
    sidewalk: SidewalkType = None
    note: str = None
    foot: AccessType = None
    bicycle_allowed: AccessType = None
    motor_vehicle_allowed: AccessType = None
    motorcycle_allowed: AccessType = None
    vehicle_allowed: AccessType = None
    horse_allowed: AccessType = None
    maxheight: float = None
    segregated: bool = None
    tracktype: str = None
    maxweight: quantity("tonne") = None
    access: AccessType = None
    surface: Surface = None
    width: quantity("meter") = None
    smoothness: str = None
    cycleway: CycleWayType = None
    right_cycleway: CycleWayType = None
    left_cycleway: CycleWayType = None
    backward_lanes: int = None
    forward_lanes: int = None
    tunnel: str = None
    footway_type: FootwayType = None
    inline_skates_allowed: AccessType = None
    exit_to: str = None
    lit: bool = None
    alt_name: str = None
    fixme: str = None
    toll: bool = None
    maxlength: int = None
    opening_date: str = None
    route: str = None
    noexit: AccessType = None
    maxspeed: int = None
    owed: AccessType = None
    comment: str = None
    waterway: WaterWayType = None
    dogs_allowed: bool = None
    goods: AccessType = None
    natural: NaturalType = None
    service: str = None
    pedestrian: bool = None
    wheelchair: WheelchairAccess = None
    proposed: RoadType = None
    noname: bool = None
    gauge: str = None
    tracks: int = None
    cutting: Cutting = None
    incline: Inclination = None
    handrail: bool = None
    end_date: str = None
    maxaxleload: float = None
    psv: AccessType = None
    crossing: CrossingType = None
    sac_scale: str = None
    trail_visibility: str = None
    covered: str = None
    ford: bool = None
    traffic_calming: TrafficCalmingType = None
    roller_ski: AccessType = None
    destination: str = None
    colour: str = None
    destination_symbol: DestinationSymbol = None
    symbol: Symbol = None
    kct_blue: bool = None
    name_1: str = None
    location: Location = None
    lane_destinations: str = None
    trolley_wire: bool = None
    proposed_bridge: bool = None
    abutters: AbuttersType = None
    embankment: bool = None
    railway_lanes_backward: str = None
    railway_lanes_forward: str = None
    ticks: float = None
    change_lanes_backward: str = None
    change_lanes_forward: str = None
    psv_lanes_backward: str = None
    psv_lanes_forward: str = None
    parking_lane_left: ParkingLaneType = None
    parking_lane_both: ParkingLaneType = None
    parking_lane_right: ParkingLaneType = None
    bus_lanes_backward: str = None
    bus_lanes_forward: str = None
    busway: Busway = None
    vehicle_lanes_backward: str = None
    vehicle_lanes_forward: str = None
    railway_lanes: str = None
    busway_right: BuswayLaneType = None
    old_name: str = None
    destination_lanes_colours: str = None
    forward_destination: str = None
    start_date: str = None
    motorcar: AccessType = None
    wikidata: str = None
    wikipedia: str = None
    tube: bool = None
    description: str = None
    material: Surface = None
    change_lanes: str = None
    traffic_zone: str = None
    maxwidth: float = None
    mtb_bicycle_class: int = None
    backward_destination: str = None
    snowplowing: bool = None
    winter_service: bool = None
    technical_mtb_bicycle_class: int = None
    narrow: bool = None
    opening_hours: str = None
    man_made: ManMade = None
    operator: str = None
    kerb: KerbType = None
    tactile_paving: TactilePaving = None
    complete: bool = None
    est_width: float = None
    snowmobile: bool = None
    level: int = None
    abandoned: bool = None
    ref_name: str = None
    ref_name_note: str = None
    placement: str = None
    is_in: str = None
    agricultural: bool = None
    carriage: bool = None
    lanes_maxwidth: float = None
    priority_road: RoadPriority = None
    lcn: bool = None
    overtaking: bool = None
    bus: AccessType = None
    pl_highway_class: str = None
    pl_highway_category: int = None
    bus_maxspeed: int = None
    trailer_maxspeed: int = None
    carriageway_width: float = None
    wet_maxspeed: int = None
    bridge_name: str = None
    variable_maxspeed: SpeedVariable = None
    sorting_name: str = None
    historic: HistoricType = None
    bus_overtaking: bool = None
    hgv_overtaking: bool = None
    trailer_overtaking: bool = None
    minspeed: int = None
    ncn: bool = None
    destination_sign: str = None
    area: bool = None
    short_name: str = None
    hgv_6_5t: AccessType = None
    destination_int_ref_lanes: str = None
    destination_ref_lanes: str = None
    destination_symbol_lanes: str = None
    left_parking_condition: ParkingCondition = None
    right_parking_condition: ParkingCondition = None
    parking_lane_both_parallel: ParkingLaneType = None
    destination_int_ref: str = None
    destination_ref: str = None
    maxspeed_type: MaxspeedType = None
    motor_vehicle_conditional: str = None
    motor_vehicle_forward_conditional: str = None
    cutline: CutlineType = None
    hgv_hour_off: str = None
    hgv_hour_on: str = None
    int_name: str = None
    parking_lane_left_diagonal: ParkingLaneType = None
    maxspeed_conditional: str = None
    forward_maxspeed_conditional: str = None
    crossing_ref: str = None
    motor_vehicle_backward: AccessType = None
    vehicle_forward: AccessType = None
    both_sidewalk_kerb: KerbType = None
    parking_lane_left_parallel: ParkingLaneType = None
    leaf_type: str = None
    # Find out what they're doing there
    vehicle_forward_conditional: str = None
    transit_lanes: str = None
    bicycle_forward_lanes: str = None
    restriction: RestrictionType = None
    wheelchair_ramp: bool = None
    hide: bool = None
    forward_maxheight: float = None
    technical_bicycle_class: int = None
    ramp: RampType = None
    survey_date: str = None
    # Make it a date
    abandoned_higway: RoadType = None
    indoor: IndoorType = None
    informal: bool = None
    ref_name_note: str = None
    ref_name: str = None
    hgv_6t: AccessType = None
    advisory_maxspeed: int = None
    old_ref: str = None
    bridge_ref: str = None
    hgv_conditional_maxspeed: str = None
    lane_marking: bool = None
    turn: str = None
    destination_country: str = None
    dual_carriageway: bool = None
    access_note: str = None
    nat_ref: str = None
    left_footway_width: float = None
    hazmat_water: bool = None
    hgv_12t: AccessType = None
    passing_places: bool = None
    sport: SportType = None
    hgv_3_5t: AccessType = None
    maxweight_note: str = None
    alt_name_de: str = None
    alt_name_en: str = None
    rcn: bool = None
    rcn_ref: int = None
    distance: float = None
    highway_area: AreaType = None
    tourism: TourismType = None
    loc_name: str = None
    place: PlaceType = None
    hazmat_e: bool = None
    destination_name: str = None
    psv_lanes: str = None
    name_note: str = None
    taxi_lanes: str = None
    disused: bool = None

    vehicle_lanes: str = None
    both_ways_lanes: int = None
    maxspeed_source: str = None
    voltage: int = None
    both_cycleway: CycleWayType = None
    vorh_parking_condition: ParkingCondition = None
    both_default_parking_condition: ParkingCondition = None
    both_residents_parking_condition: int = None
    both_parking_condition_time_interval: str = None
    zone_maxspeed: int = None
    psv_oneway: bool = None
    removed_cycleway: CycleWayType = None
    incline_steep: bool = None
    bicycle_lanes: str = None
    hazmat: bool = None
    amenity: Amenity = None
    ski: bool = None
    tourist_bus: bool = None
    pedestrians: bool = None
    hgv_maxweight: int = None
    priority: RoadPriority = None
    hgv_lanes: str = None
    fee: str = None
    reg_name_note: str = None
    reg_name: str = None
    cs_note: str = None
    height: quantity("meter") = None
    repeat_on: str = None
    stroller: bool = None

    bdouble: bool = None
    shoulder: ShoulderType = None
    both_parking_condition: str = None
    hazard: Hazard = None
    divider: Divider = None
    kct_green: RouteImportance = None
    bus_lanes: int = None
    his_1991_name: str = None
    conditional_overtaking: str = None
    horse_suitable: bool = None
    veh_ban_from: str = None
    emergency: EmergencyType = None
    hgv_backward_conditional_maxspeed: str = None
    hgv_backward: AccessType = None
    electrified: str = None
    forward_overtaking: bool = None
    hgv_backward_maxspeed: int = None
    support: Support = None
    right_parking_condition_time_interval: str = None
    parking_lane: ParkingLaneType = None
    official_name: str = None
    his_1945_name: str = None
    both_residents_parking_condition_time_interval: str = None
    odbl: ODBL = None
    forward_placement: str = None
    backward_overtaking: bool = None
    his_1896_name: str = None
    both_parking: str = None
    his_1400_1800_name: str = None
    his_1870_1940_name: str = None
    backward_bus: AccessType = None
    shelter: bool = None
    indoor_level: str = None
    backward_change: bool = None
    junction_ref: int = None
    capacity: int = None
    right_parking_condition_maxstay: str = None
    destination_note: str = None
    barrier: BarrierType = None
    right_residents_parking_condition: int = None
    destination_street: str = None
    left_arcade: ArcadeType = None
    conditional_maxwidth: str = None
    his_1930_name: str = None
    tmc_cid_58_tabcd_1_class: TMC_CID_58_TABCD_1_Class = None
    tmc_cid_58_tabcd_1_lclversion: float = None
    tmc_cid_58_tabcd_1_nextlocationcode: int = None
    hgv_conditional_overtaking: str = None
    psv_lanes_times: str = None
    his_1990_name: str = None
    check_date: str = None
    his_1962_name: str = None
    stroller_ramp: bool = None
    depth: float = None
    forward_hazard: str = None
    both_sidewalk_surface: Surface = None
    conveying: Conveying = None
    his_1940_1945_name: str = None
    right_parking_default_condition: ParkingCondition = None
    hgv_12: AccessType = None
    alt_name_cs: str = None
    abandoned_railway: RailWayType = None
    his_1840_1870_name: str = None
    tram: bool = None
    his_1951_1990_name: str = None
    length: int = None
    attraction: bool = None
    website: str = None
    sloped_curb: CurbType = None
    bridge_height: int = None
    oneway_railway: bool = None
    building: BuildingType = None
    proposed_highway: RoadType = None
    taxi_lanes_forward: str = None
    destination_colour_tx_lanes: str = None
    max: int = None
    surface_1: Surface = None
    right_bicycle_sidewalk: bool = None
    left_bicycle_sidewalk: bool = None
    abandoned_highway: RoadType = None
    backward_conditional_maxspeed: str = None
    traffic_sign: TrafficSignType = None
    description_ref: str = None
    hgv_tolltype: str = None
    maxheight_note: str = None
    steps: bool = None







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

    def __str__(self):
        retval = super().__str__()
        if self.type:
            retval += " ({})".format(underscored_to_words(self.type.name))
        return retval