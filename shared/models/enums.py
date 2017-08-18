import enum

class AccessType(enum.Enum):
    unspecified = -1
    no = 0
    yes = 1
    customers = 2
    destination = 3
    private = 4
    permissive = 5
    forestry = 6
    delivery = 7
    designated = 8
    public = 9
    dismount = 10

class LeisureType(enum.Enum):
    none = 0
    swimming_pool = 1
    park = 2
    stadium = 3
    sports_centre = 4
    cinema = 5
    pitch = 6
    common = 7
    track = 8
    playground = 9
    water_park = 10
    picnic_table = 11
    recreation_ground = 12
    bird_hide = 13
    firepit = 14
    dog_park = 15
    nature_reserve = 16
    golf_course = 17
    disc_golf_course = 18
    ice_rink = 19
    garden = 20
    fitness_centre = 21

class Amenity(enum.Enum):
    none = 0
    restaurant = 1
    place_of_worship = 2
    school = 3
    kindergarten = 4
    bus_station = 5
    cinema = 6
    college = 7
    hospital = 8
    pharmacy = 9
    library = 10
    toilets = 11
    townhall = 12
    police = 13
    fast_food = 14
    post_office = 15
    fire_station = 16
    bench = 17
    waste_basket = 18
    telephone = 19
    community_centre = 20
    car_wash = 21
    cafe = 22
    vending_machine = 23
    bar = 24
    doctors = 25
    childcare = 26
    mountain_rescue = 27
    exhibition_hall = 28
    parking_entrance = 29
    biergarten = 30
    hunting_stand = 31
    university = 32
    clock = 33
    veterinary = 34
    bicycle_parking = 35
    bbq = 36 # A barbecue grill
    marketplace = 37
    taxi = 38
    drinking_water = 39
    brothel = 40
    driving_school = 41
    music_venue = 42
    nightclub = 43
    crematorium = 44
    parking_space = 45
    courthouse = 46
    dentist = 47
    parking = 48
    monastery = 49
    nursing_home = 50
    public_building = 51
    prison = 52
    fuel = 53
    theatre = 54
    arts_centre = 55
    dive_centre = 56
    waste_disposal = 57
    feeding_place = 58
    clinic = 59



class ShopType(enum.Enum):
    none = 0
    unknown = 0
    supermarket = 1
    doityourself = 2
    kiosk = 3
    car = 4
    funeral_directors = 5
    bicycle = 6
    alcohol = 7
    garden_centre = 8
    convenience = 9
    optician = 10
    confectionery = 11
    chemist = 12
    clothes = 13
    car_repair = 14
    electronics = 15
    bakery = 16
    sports = 17
    hairdresser = 18
    computer = 19
    toys = 20
    florist = 21
    motorcycle = 22
    furniture = 23
    wine = 24
    tyres = 25
    books = 26
    outdoor = 27
    coffee = 28
    general = 29
    greengrocer = 30
    gift = 31
    newsagent = 32
    mobile_phone = 33
    shoes = 34
    stationery = 35
    plastic_modlings = 36
    mall = 37
    department_store = 38
    laundry = 39
    car_parts = 40
    yes = 41
    paint = 42
    hardware = 43
    pastry = 44
    scuba_diving = 45
    
class Inclination(enum.Enum):
    unknown = 0
    up = 1
    down = 2
    yes = 3
    forward = 4

class ManMade(enum.Enum):
    none = 0
    water_tower = 1
    reservoir_covered = 2
    chimney = 3
    wastewater_plant = 4
    bridge = 5
    works = 6
    water_well = 7
    survey_point = 8
    tower = 9
    pipeline = 10
    pier = 11
    cutline = 13
    cliff = 14
    observatory = 15
    crane = 16
    surveillance = 17
    cellar_entrance = 18


class SportType(enum.Enum):
    none = 0
    tennis = 1
    soccer = 2
    roller_skating = 3
    multi = 4
    ice_skating = 5
    running = 6
    skateboard = 7
    cycling = 8
    beachvolleyball = 9
    boules = 10
    badminton = 11
    nine_pin = 12
    golf = 13
    ten_pin = 14
    climbing = 15
    swimming = 16
    skiing = 17
    karting = 18
    athletics = 17
    baseball = 18
    ice_hockey = 19
    squash = 20
    volleyball = 21
    basketball = 22
    equestrian = 23
    shooting = 24
    disc_golf = 25
    shooting_range = 26
    skiing_cycling = 27
    ski_jumping = 28

class BarrierType(enum.Enum):
    none = 0
    wall = 1
    gate = 2
    turnstile = 3
    bollard = 4
    lift_gate = 5
    cycle_barrier = 6
    full_height_turnstile = 7
    block = 8
    swing_gate = 9
    entrance = 10
    fence = 11
    cattle_grid = 12
    kissing_gate = 13 # Really?
    guard_rail = 14
    hedge = 15
    retaining_wall = 16
    handrail = 17
    jersey_barrier = 18
    toll_booth = 19
    kerb = 20
    
class SmokingType(enum.Enum):
    none = 0
    outside = 1
    yes = 2
    no = 3
    separated = 4
    
class TourismType(enum.Enum):
    none = 0
    attraction = 1
    camp_site = 2
    information = 3
    viewpoint = 4
    guest_house = 5
    museum = 6
    hotel = 7
    picnic_site = 8
    artwork = 9
    hostel = 10
    theme_park = 11
    alpine_hut = 12
    motel = 13
    gallery = 14
    zoo = 15
    yes = 16
    
    
class CrossingType(enum.Enum):
    no = -1
    unknown = 0
    island = 1
    uncontrolled = 2
    zebra = 3 #Cz specific?
    traffic_signals = 4
    unmarked = 5
    crossing = 6
    island_ucontrolled = 7

class HistoricType(enum.Enum):
    none = -1
    wayside_shrine = 0
    memorial = 1
    wayside_cross = 2
    ruins = 3
    monument = 4
    boundary_stone = 5
    castle = 6
    archaeological_site = 7


class TrafficCalmingType(enum.Enum):
    none = 0
    yes = 1
    bump = 2
    ditch = 3
    hump = 4 # Should find out if it is a typo or not
    dip = 5
    rumble_strip = 6
    table = 7
    chicane = 8

class WaterWayType(enum.Enum):
    none = 0
    canal = 1
    stream = 2
    river = 3
    riverbank = 4
    weir = 5
    dam = 6
    ditch = 7
    drain = 8


class NaturalType(enum.Enum):
    none = -1
    wetland = 0
    scrub = 1
    wood = 2
    scree = 3
    spring = 4
    peak = 5
    tree = 6
    saddle = 7
    stone = 8
    rock = 9
    cave_entrance = 10
    water = 11
    tree_row = 12
    bare_rock = 13
    cliff = 14
    ridge = 15
    grass = 16
    beach = 17
    grassland = 18
    shingle = 19

class BuildingType(enum.Enum):
    none = -1
    unknown = 0
    yes = 1
    residential = 2
    transportation = 3
    civic = 4
    train_station = 5

class InfoType(enum.Enum):
    none = 0
    guidepost = 1
    office = 2
    map = 3
    board = 4
    

class AerialWayType(enum.Enum):
    none = -1
    platter = 0
    helipad = 1
    pylon = 2
    windsock = 3
    cable_car = 4
    station = 5
    aerodrome = 6
    taxiway = 7
    chair_lift = 8
    runway = 9
    drag_lift = 10
    lift = 11


class RailWayType(enum.Enum):
    none = -1
    rail = 0
    abandoned = 1
    turntable = 2
    level_crossing = 3
    buffer_stop = 4
    halt= 5
    crossing = 6
    station = 7
    switch = 8
    tram = 9
    preserved = 10
    platform = 11
    railway_crossing = 12
    narrow_gauge = 13
    service_station = 14

class TunnelType(enum.Enum):
    no = 0
    yes = 1
    culvert = 2
    building_passage = 3

class BridgeType(enum.Enum):
    no = 0
    yes = 1
    viaduct = 2

class RoadType(enum.Enum):
    none = -1
    unclassified = 0
    trunk = 1
    primary = 2
    secondary = 3
    tertiary = 4
    trunk_link = 5
    primary_link = 6
    residential = 7
    service = 8
    footway = 9
    track = 10
    path = 11
    cycleway = 12
    living_street = 13
    pedestrian = 14
    secondary_link = 15
    turning_circle = 17
    traffic_signals = 18
    motorway_junction = 19
    traffic_mirror = 20
    ford = 21
    street_lamp = 22
    passing_place = 23
    mini_roundabout = 24
    construction = 25
    tertiary_link = 26
    bridleway = 27
    road = 28
    proposed = 29
    speed_camera = 30
    stop = 31

class LandType(enum.Enum):
    forest = 0
    reservoir = 1
    residential = 2
    industrial = 3
    commercial = 4
    grass = 5
    cemetery = 6
    farmland = 6
    meadow = 7
    orchard = 8
    railway = 9
    allotments = 10
    village_green = 11
    garages = 12
    quarry = 13
    military = 14
    brownfield = 15
    landfill = 16
    recreation_ground = 17
    plant_nursery = 18
    shingle = 19
    retail = 20

class BuildingPartType(enum.Enum):
    yes = 0
    civic = 1
    industrial = 2

class RoofShape(enum.Enum):
    flat = 0
    pyramidal = 1
    hipped = 2

class Location(enum.Enum):
    indoor = 0