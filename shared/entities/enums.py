import enum

class OSMObjectType(enum.Enum):
    node = "node"
    way = "way"
    relation = "relation"

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
    openhour = 11
    disabled = 12
    psv = 13
    agricultural = 14
    hgv = 15
    unknown = 16
    official = 17
    restricted = 18
    emergency = 19
    dedicated = 20
    t = 21
    permission = 22
    mtb = 23
    use_sidepath = 24
    on_request = 25
    opposite = 26
    destinaton = 27
    limited = 28



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
    bleachers = 22
    hackerspace = 23
    horse_riding = 24
    table_tennis_table = 25
    sauna = 26
    fitness_station = 27
    tanning_salon = 28
    dance = 29
    yes = 30
    miniature_golf = 31
    marina = 32
    maze = 33
    slipway = 34
    badminton = 35
    social_club = 36
    adult_gaming_centre = 37
    amusement_arcade = 38
    meadow = 39
    sport = 40
    beach_resort = 41
    outdoor_seating = 42
    long_jump = 43
    racetrack = 44
    swimming_area = 45
    me = 46
    bowling_alley = 47
    multipolygon = 48



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
    bbq = 36
    # A barbecue grill
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
    swimming_pool = 60
    ice_cream = 61
    bycicle_rental = 62
    embassy = 63
    grit_bin = 64
    ferry_terminal = 65
    fodder_rack = 66
    food_court = 67
    compressed_air = 68
    pub = 69
    bureau_de_change = 70
    charging_station = 71
    feeding_rack = 72
    ticket_validator = 73
    baby_hatch = 74
    bycicle_repair_station = 75
    public_bookcase = 76
    vehicle_inspection = 77
    casino = 78
    car_rental = 79
    first_aid = 80
    boat_rental = 81
    retirement_home = 82
    animal_shelter = 83
    music_school = 84
    dog_training = 85
    exhibition_center = 86
    proposed = 87
    coworking_space = 88
    canteen = 89
    wine_bar = 90
    dog_asylum = 91
    authority = 92
    charity = 93
    bicycle_rental = 94
    other = 95
    gambling = 96
    hospice = 97
    winery = 98
    board_games_club = 99
    menza = 100
    stripclub = 101
    conference_centre = 102
    animal_training = 103
    dormitory = 104
    dojo = 105
    stock_exchange = 106
    studio = 107
    bicycle_repair_station = 108
    feeder = 109
    vacuum_cleaner = 110
    shower = 111
    loading_dock = 112
    concert_hall = 113
    sauna = 114
    table = 115
    shop = 116
    trolley_bey = 117
    construction = 118
    left_luggage = 119
    photo_booth = 120
    planetarium = 121
    art_school = 122
    science = 123
    station = 124
    park = 125
    social_centre = 126
    bag_wrap = 127
    seating = 128
    check_in = 129
    reception_desk = 130
    yes = 131
    luggage_locker = 132
    bts = 133
    elevator = 134
    academy = 135
    residential = 136
    trolley_bay = 137
    architect_office = 138
    customs = 139
    stairs = 140
    office = 141
    brewery = 142
    love_hotel = 143




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
    jewelry = 46
    butcher = 47
    interior_decoration = 48
    fashion = 49
    copyshop = 50
    pet = 51
    vacant = 52
    chemistry = 53
    seafood = 54
    musical_instrument = 55
    organic = 56
    tailor = 57
    fabric = 58
    frame = 59
    hifi = 60
    art = 61
    pawnbroker = 62
    antiques = 63
    hobby = 64
    cooking = 65
    boutique = 66
    fishing = 67
    bathroom = 68
    beverages = 69
    herbalist = 70
    clocks = 71
    dry_cleaning = 72
    watch = 73
    locksmith = 74
    travel_agency = 75
    music = 76
    fishmonger = 77
    perfumery = 78
    massage = 79
    deli = 80
    outdoor_hunting = 81
    bag = 82
    isp = 83
    beauty = 84
    cosmetics = 85
    coins = 86
    food = 87
    weapons = 88
    medical_supply = 89
    video = 90
    nutrition_supplements = 91
    houseware = 92
    photo = 93
    beer = 94
    variety_store = 95
    erotic = 96
    cheese = 97
    baby_goods = 98
    bathroom_furnishing = 99
    carpet = 100
    kitchen = 101
    trade = 102
    games = 103
    tea = 104
    bed = 105
    ticket = 106
    ice_cream = 107
    souvenir = 108
    vacuum_cleaner = 109
    curtain = 110
    estate_agent = 111
    tobacco = 112
    sewing = 113
    bookmaker = 114
    tiles = 115
    electrical = 116
    wood_floor = 117
    radiotechnics = 118
    no = 119
    craft = 120
    grocery = 121
    glass = 122
    military = 123
    lighting = 124
    appliances = 125
    locks_and_keys = 126
    ski = 127
    painter = 128
    glaziery = 129
    stonework = 130
    furniture_interior_decoration = 131
    photoshop = 132
    shoe_repair = 133
    stationery_chemist = 134
    drogist = 135
    watches = 136
    models = 137
    fireworks = 138
    children = 139
    fairtrade = 140
    lost_and_found = 141
    empty = 142
    medical_equipment = 143
    second_hand = 144
    handicraft = 145
    hunting = 146
    energy = 147
    crystal = 148
    leather = 149
    army = 150
    betting = 151
    spiritual = 152
    electronics_stationery = 153
    farm = 154
    Karavany = 155
    money_lender = 156
    insurance = 157
    supplements = 158
    shoemaker = 159
    software = 160
    lottery = 161
    copyshop_toys = 162
    #plavecké_potřeby = 163
    eBikes = 164
    rc_models = 165
    video_games = 166
    Apple_service_and_accessories = 167
    tattoo = 168
    plumber = 169
    duty_free = 170
    hairdresser_beauty = 171
    beekeeping = 172
    fireplace = 173
    hearing_aids = 174
    haberdashery = 175
    window_blind = 176
    lamps = 177
    #výroba_reklamy = 178
    glassware = 179
    bathroom_furniture = 180
    mushrooms = 181
    italian_food = 182
    greek = 183
    chocolate = 184
    floorer = 185
    design = 186
    sewing_machines = 187
    carpeting = 188
    auto_repair = 189
    model = 190
    
    
    
class Inclination(enum.Enum):
    unknown = 0
    up = 1
    down = 2
    yes = 3
    forward = 4
    backward = 5
    no = 6
    anticlockwise = 7
    
    

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
    adit = 19
    mast = 20
    fodder_rack = 21
    reservoir = 22
    watermill = 23
    water_works = 24
    flagpole = 25
    beacon = 26
    beehive = 27
    dyke = 28
    street_cabinet = 29
    cross = 30
    campanile = 31
    yes = 32
    advertising = 33
    insect_hotel = 34
    monitoring_station = 35
    embankment = 36
    bunker_silo = 37
    cooling_tower = 38
    pillar = 39
    communications_tower = 40
    antenna = 41
    storage_tank = 42
    windsock = 43
    telescope = 44
    lighthouse = 45
    stack = 46
    fire_reserve = 47
    gasometer = 48
    silo = 49
    clearcut = 50
    canopy = 51
    windmill = 52
    wayside_shrine = 53
    mineshaft = 54





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
    gymnastics = 29
    fitness = 30
    table_tennis = 31
    fishing = 32
    archery = 33
    box = 34
    bowling = 35
    trampoline = 36
    dance = 37
    chess = 38
    paintball = 39
    petanque = 40
    exercise = 41
    toboggan = 42
    rowing = 43
    laser_tag = 44
    handball = 45
    floorball = 46
    hockey = 47
    rugby = 48
    hockeyball = 49
    rugby_league = 50
    horse_racing = 51
    skating = 52
    softball = 53
    canoe = 54
    bmx = 55
    american_football = 56
    motor = 57
    parkour = 58
    cycling_skiing = 59
    sokol = 60
    rugby_union = 61
    boxing = 62
    ropes_course = 63
    scuba_diving = 64
    snowboarding = 65
    billiards = 66
    bowls = 67
    yoga = 68
    kettlebell = 69
    climbing_adventure = 70
    miniature_golf = 71
    dog_racing = 72
    team_handball = 73
    football = 74
    field_hockey = 75
    bobsleigh = 76
    minigolf = 77
    motocross = 78
    workout = 79
    dog_training = 80
    fire_fighting = 81
    curling = 82
    kanoistika = 83
    riding = 84
    climbing_wall = 85
    rc_car = 86
    hardcourt_bikepolo = 87
    long_jump = 88
    footbal = 89
    model_aerodrome = 90
    aikido = 91
    jumping = 92




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
    kissing_gate = 13
    # Really?
    guard_rail = 14
    hedge = 15
    retaining_wall = 16
    handrail = 17
    jersey_barrier = 18
    toll_booth = 19
    kerb = 20
    portcullis = 21
    hampshire_gate = 22
    stile = 23
    chain = 24
    wire = 25
    log = 26
    yes = 27
    height_restrictor = 28
    city_wall = 29
    wire_fence = 30
    railing = 31
    sally_port = 32
    rope = 33
    banister = 34
    glass = 36
    border_control = 37
    recommended = 38
    no = 39
    ramp = 40




class SmokingType(enum.Enum):
    none = 0
    outside = 1
    yes = 2
    no = 3
    separated = 4
    isolated = 5
    dedicated = 6


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
    chalet = 17
    caravan_site = 18
    disused = 19
    apartment = 20
    wine_cellar = 21
    
    
    
    
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
    marked = 8
    surface = 9
    yes = 10
    bicycle = 11
    cycle = 12
    controlled = 13
    
    
    
    

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
    tomb = 8
    yes = 9
    monastery = 10
    quarry = 11
    city_gate = 12
    attraction = 13
    battlefield = 14
    restaurant = 15
    aircraft = 16
    building = 17
    tank = 18
    highwater_mark = 19
    garages = 20
    heritage = 21
    border_control = 22
    railway = 23
    palace = 24
    gate = 25
    stone = 26






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
    island = 9
    cushion = 10
    

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
    waterfall = 9
    wadi = 10
    lock_gate = 11
    boatyard = 12
    lock = 13
    dock = 14




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
    heath = 20
    sand = 21
    bedrock = 22
    sinkhole = 23
    mud = 24
    valley = 25
    hill = 26



class BuildingType(enum.Enum):
    none = -1
    unknown = 0
    yes = 1
    residential = 2
    transportation = 3
    civic = 4
    train_station = 5
    house = 6
    garage = 7
    roof = 8
    warehouse = 9
    industrial = 10
    commercial = 11
    shelter = 12
    railway_station = 13
    apartments = 14
    cabin = 15
    garages = 16
    service = 17
    transformer_tower = 18
    ruins = 19
    construction = 20



class InfoType(enum.Enum):
    none = 0
    guidepost = 1
    office = 2
    map = 3
    board = 4
    history = 5
    plants = 6
    terminal = 7
    tree = 8
    bicyclemap = 9
    nature = 10
    
    
    

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
    apron = 12
    terminal = 13
    hangar = 14
    holding_position = 15
    navigationaid = 16
    gate = 17
    papi = 18
    parking_position = 19
    proposed = 20
    
    


class RailWayType(enum.Enum):
    none = -1
    rail = 0
    abandoned = 1
    turntable = 2
    level_crossing = 3
    buffer_stop = 4
    halt = 5
    crossing = 6
    station = 7
    switch = 8
    tram = 9
    preserved = 10
    platform = 11
    railway_crossing = 12
    narrow_gauge = 13
    service_station = 14
    junction = 15
    disused = 16
    razed = 17
    proposed = 18
    dismantled = 19
    miniature = 20
    railway = 21
    subway_entrance = 22
    signal = 23
    crossover = 24
    subway = 25
    construction = 26
    funicular = 27
    roundhouse = 28
    yes = 29
    signal_box = 30
    stop = 31
    milestone = 32
    border = 33
    defect_detector = 34
    isolated_track_section = 35
    traverser = 36
    staton = 37
    site = 38
    workshop = 39




class TunnelType(enum.Enum):
    no = 0
    yes = 1
    culvert = 2
    building_passage = 3
    avalanche_protector = 4
    

class BridgeType(enum.Enum):
    no = 0
    yes = 1
    viaduct = 2
    culvert = 3
    covered = 4
    boardwalk = 5
    trestle = 6
    cantilever = 7
    
    
    

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
    incline_steep = 32
    trolleybus_stop = 33
    elevator = 34
    speed_radar = 35
    motorway = 36
    motorway_link = 37
    raceway = 38
    platform = 39
    corridor = 40
    yes = 41
    abandoned = 42
    traffic_island = 43
    give_way = 44
    milestone = 45
    emergency_access_point = 46
    turning_loop = 47
    services = 48
    rest_area = 49
    emergency_bay = 50
    virtual = 51
    stop_line = 52
    toll_bridge = 53
    speed_display = 54
    bus_stop = 55
    contruction = 56
    steps = 57
    camera = 58




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
    basin = 21
    construction = 22
    farmyard = 23
    greenfield = 24
    proposed = 25
    highway = 26
    vineyard = 27
    greenhouse_horticulture = 28
    animal_keeping = 29
    garden = 30
    paddock = 31
    churchyard = 32
    yes = 33
    river = 34
    playground = 35
    flowerbed = 36
    park = 37
    community_food_growing = 38
    vliage_grenn = 39



class BuildingPartType(enum.Enum):
    yes = 0
    civic = 1
    industrial = 2
    balcony = 3
    garages = 4
    residential = 5
    tower = 6
    ramp = 7
    elevator = 8
    steps = 9
    roof = 10
    column = 11
    chimney = 12
    wall = 13
    commercial = 14
    greenhouse = 15
    garage = 16



class RoofShape(enum.Enum):
    flat = 0
    pyramidal = 1
    hipped = 2
    gabled = 3
    skillion = 4
    sawtooth = 5
    dome = 6
    round = 7
    gambrel = 8
    mansard = 9
    onion = 10
    side_hipped = 11
    saltbox = 12
    tripple_skillion = 13
    pitched = 14
    triple_skillion = 15
    ga = 16
    yes = 17
    pyrmidal = 18
    tile = 19
    many = 20



class Location(enum.Enum):
    indoor = 0
    underground = 1
    kiosk = 2
    outdoor = 3
    overground = 4
    bridge = 5

class BridgeStructure(enum.Enum):
    beam = 1
    arch = 2
    truss = 3
    humpback = 4
    suspension = 5
    simple_suspension = 6


class Role(enum.Enum):
    outer = 0
    inner = 1
    guidepost = 2
    route = 3
    platform = 4
    stop = 5
    admin_centre = 6
    subarea = 7
    outline = 8
    forward = 9
    backward = 10
    to = 11
    line = 12
    building = 13
    main_stream = 14
    substation = 15
    from_ = 16
    part = 17
    landuse = 18
    generator = 19
    link = 20
    via = 21
    service_station = 22
    address = 23
    platform_exit_only = 24
    entrance = 25
    information = 26
    yard = 27
    station = 28
    halt = 29
    service_yard = 30
    tram_stop = 31
    map = 32
    backward_stop = 33
    platform_on_demand = 34
    alternate = 35
    forward_stop = 36
    bus_stop = 37
    stop_on_demand = 38
    across = 39
    under = 40
    board = 41
    stop_entry_only = 42
    stop_exit_only = 43
    proposed = 44
    house = 45
    platform_entry_only = 46
    through = 47
    shelter = 48
    device = 49
    buildingpart = 50
    side_stream = 51
    sub_station = 52
    excursion = 53
    entrance_exit = 54
    end = 55
    alternation = 56
    stop_position = 57
    level_1 = 58
    street = 59
    shell = 60
    stop_area = 61
    perimeter = 62
    begin = 63
    parking = 64
    stop_2 = 65
    stop_10 = 66
    stop_14 = 67
    MHD = 68
    reception = 69
    hostel = 70
    stop_1 = 71
    stop_0_backward = 72
    label = 73
    place_of_worship = 74
    stop_32 = 75



class ConstructionType(enum.Enum):
    railway = 0
    motorway = 1
    motorway_link = 2
    restaurant = 3
    information = 4
    residential = 5
    retail = 6
    building = 7
    garages = 8
    terrace = 9
    yes = 10
    commercial = 11
    apartments = 12
    office = 13
    hotel = 14
    house = 15
    transportation = 16
    parking = 17
    bus_stop = 18
    reatil = 19


class IndustrialType(enum.Enum):
    factory = 0
    distributor = 1
    power = 2
    depot = 3
    brewery = 4


class RoofOrientation(enum.Enum):
    across = 0
    along = 1
    

class Surface(enum.Enum):
    dirt = 0
    concrete = 1
    asphalt = 2
    grass = 3
    clay = 4
    sand = 5
    artificial_grass = 6
    tartan = 7
    gravel = 8
    unpaved = 9
    plastic = 10
    ground = 11
    paved = 12
    paving_stones = 13
    cobblestone = 14
    sett = 16
    compacted = 17
    wood = 18
    steel = 19
    fine_gravel = 20
    mud = 21
    concrete_slabs = 22
    yes = 23
    metal = 24
    grass_paver = 25
    earth = 26
    rocks = 27
    stone = 28
    pebblestone = 29
    panel = 30
    pannel = 31
    artificial_turf = 32
    concrete_plates = 33
    brash = 34
    asp = 35
    set = 36
    ettand = 37
    metal_grid = 38
    rubber = 39
    sd = 40
    soil = 41
    tiled = 42
    synthetic_turf = 43


class ReservationType(enum.Enum):
    yes = 1
    recommended = 2
    no = 3

class WifiType(enum.Enum):
    no = 0
    yes = 1
    free = 2


class GolfRelation(enum.Enum):
    bunker = 0
    green = 1
    driving_range = 2

class KerbType(enum.Enum):
    lowered = 1
    raised = 2

class WheelchairAccess(enum.Enum):
    no = 0
    yes = 1
    limited = 2
    unknown = 3


class SidewalkType(enum.Enum):
    unknown = 0
    left = 1
    right = 2
    both = 3
    no = 4
    separate = 5
    none = 6
    


class RoofMaterial(enum.Enum):
    roof_tiles = 0
    tin = 1
    tile = 2
    glass = 3
    tar_paper = 4
    copper = 5
    metal = 6
    concrete = 7
    stone = 8
    slate = 9
    gravel = 10
    grass = 11
    limestone = 12
    plaster = 13
    wood = 14
    plastic = 15
    sandstone = 16
    linestone = 17

class SurveillanceType(enum.Enum):
    none = 0
    public = 1
    outdoor = 2
    indoor = 3
    webcam = 4
    

class FenceType(enum.Enum):
    chain_link = 0
    electric = 1
    chain = 2
    wire = 3
    metal = 4
    wood = 5
    corrugated_metal = 6
    balustrade = 7
    railing = 8
    bars = 9


class ParkingType(enum.Enum):
    multipolygon = 0
     # Map it to unspecified
    surface = 1
    multi_storey = 2
    underground = 3
    rooftop = 4
    asphalt = 5
    lane = 6
    kiss_and_ride = 7
    garage = 8
    carports = 9
    sheds = 10
    yes = 11

class RestrictionType(enum.Enum):
    no_right_turn = 0
    only_right_turn = 1
    only_straight_on = 2
    no_left_turn = 3
    no_u_turn = 4
    restriction = 5
    no_straight_on = 6
    only_left_turn = 7
    no_exit = 8



class RouteType(enum.Enum):
    hiking = 1
    bicycle = 2
    tracks = 3
    train = 4
    road = 5
    power = 6
    foot = 7
    ski = 8
    bus = 9
    trolleybus = 10
    tram = 11
    abandoned = 12
    railway = 13
    wheelchair = 14
    mtb = 15
    ferry = 16
    route = 17
    subway = 18
    tourist_train = 19
    light_rail = 20
    running = 21
    funicular = 22



class SurveillanceKind(enum.Enum):
    guard = 0
    camera = 1

class SurveillanceZone(enum.Enum):
    building = 0
    town = 1
    traffic = 2
    parking = 3
    gate = 4

class IndoorType(enum.Enum):
    room = 0
    level = 1
    area = 2
    no = 3
    yes = 4
    corridor = 5


class AreaType(enum.Enum):
    unclassified = 0
    pedestrian = 1
    platform = 2
    service = 3
    yes = 4
    path = 5
    footway = 6
    rest_area = 7
    living_street = 8
    residential = 9
    track = 10
    construction = 11
    elevator = 12

class PlaceType(enum.Enum):
    village = 0
    hamlet = 1
    suburb = 2
    town = 3
    locality = 4
    city = 5
    neighbourhood = 6
    islet = 7
    island = 8
    square = 9
    farm = 10
    isolated_dwelling = 11
    country = 12

class AttractionType(enum.Enum):
    animal = 0
    water_slide = 1
    fossils = 2

class TransformerType(enum.Enum):
    distribution = 0
    traction = 1
    minor_distribution = 2

class TrailVisibility(enum.Enum):
    excellent = 0
    good = 1
    intermediate = 2

class ResidentialType(enum.Enum):
    urban = 0
    university = 1

class MemorialKind(enum.Enum):
    unknown = 0
    war_memorial = 1
    plaque = 2
    statue = 3
    bust = 4
    stele = 5
    tablet = 6
    stone = 7
    artwork = 8
    bas_relief = 9
    memorial = 10


class GardenType(enum.Enum):
    residential = 0
    botanical = 1
    monastery = 2
    castle = 3
    arboretum = 4
    residentia = 5
    residental = 6

class RouteImportance(enum.Enum):
    major = 0
    local = 1
    learning = 3
    ruin = 4
    peak = 5
    spring = 6
    interesting_object = 7
    horse = 8
    ski = 9
    bicycle = 10
    wheelchair = 11

class EmergencyType(enum.Enum):
    no = 0
    yes = 1
    ambulance_station = 2
    access_point = 3

class Support(enum.Enum):
    wall_mounted = 0
    pedestal = 1
    pole = 2

class NoticeFunction(enum.Enum):
    prohibition = 1
    information = 2
    restriction = 3

class NoticeType(enum.Enum):
    notice = 0
    small_craft_facility = 1

class MemorialType(enum.Enum):
    unknown = 0
    plaque = 1
    stolperstein = 2
    statue = 3
    plate = 4
    war_memorial = 5
    
class Material(enum.Enum):
    glass = 0
    steel = 1
    stone = 2
    concrete = 3
    brick = 4
    wood = 5
    limestone = 6
    tiles = 7
    sandstone = 8
    mdf = 9
    granite = 10
    mirror = 11
    plastic = 12
    metal = 13
    bronze = 14
    rope = 15
    ground = 16

class ArtWorkType(enum.Enum):
    statue = 0
    architecture = 1
    sculpture = 2
    mural = 3
    photo = 4
    tower = 5
    installation = 6
    relief = 7
    topiary = 8
    graffiti = 9
    bust = 10

class AdvertisingType(enum.Enum):
    billboard = 0
    totem = 1
class NoticeImpact(enum.Enum):
    upstream = 1
    downstream = 2
    right_bank = 3

class LandCover(enum.Enum):
    grass = 0
    water = 1

class NoticeCategory(enum.Enum):
    no_passage_left = 1
    no_passage_right = 2
    no_anchoring = 3
    berthing_permitted = 4
    limited_headroom = 5
    channel_distance_right = 6
    no_wash = 7
    weir = 8
    no_entry = 9
    channel_distance_left = 10
    no_berthing = 11
    turning_area = 12

class InternetAccess(enum.Enum):
    yes = 0
    wlan = 1

class SiteType(enum.Enum):
    site = 0
    stop_area = 1
    settlement = 2
    fortification = 3
    stree = 4

class CurbType(enum.Enum):
    no = 0
    yes = 1
    both = 2

class Service(enum.Enum):
    alley = 0
    parking_aisle = 1

class Direction(enum.Enum):
        north = 0
        south = 1
        backward = 2
        forward = 3
        west = 4
        SW = 5
        S = 6
        NE = 7
        NW = 8
        SSE = 9
        E = 10
        WNW = 11
        SE = 12
        WSW = 13
        W = 14
        ENE = 15


class ToiletsDisposal(enum.Enum):
    flush = 0
    chemical = 1

class FastFoodType(enum.Enum):
    yes = 0
    cafeteria = 1

class DiplomacyRelation(enum.Enum):
    ambassadors_residence = 0
    embassy = 1
    ambassadors_resaidence = 2

class DietType(enum.Enum):
    no = 0
    yes = 1
    only = 2

class BicycleType(enum.Enum):
    no = 0
    yes = 1
    dismount = 2
    designated = 3


class Denomination(enum.Enum):
    roman_catholic = 0
    catholic = 1
    evangelical = 2

class TrafficSignType(enum.Enum):
    city_limit = 0
    maxspeed = 1

class EntranceType(enum.Enum):
    main = 0
    yes = 1
    service = 2
    emergency = 3
    home = 4
    private = 5
    exit = 6
    garage = 7
    entrance = 8
    gate = 9


class PowerSubstationType(enum.Enum):
    unspecified = 0
    distribution = 1
    industrial = 2
    minor_distribution = 3
    traction = 4
    transmission = 5
    

class GeneratorSource(enum.Enum):
    unknown = 0
    hydro = 1
    solar = 2
    solar_photovoltaic_panel = 3
    gas = 4

class MilitaryType(enum.Enum):
    none = 0
    barracks = 1
    danger_area = 2
    checkpoint = 3
class PowerType(enum.Enum):
    tower = 0
    substation = 1
    portal = 2
    station = 3
    transformer = 4
    cable_distribution_cabinet = 5
    minor_line = 6
    cable = 7
    insulator = 8
    terminal = 9
    switch = 10
    transition = 11
    sub_station = 12
    switchgear = 13
    pole = 14
    

class TowerType(enum.Enum):
    unknown  = 0
    communication = 1
    observation = 2
    climbing = 3
    bell_tower = 4
    bts = 5
    lighting = 6
    church = 7
    cooling = 8
    campanile = 9
    meteo = 10
    fire = 11
    anchor = 12




class ShelterType(enum.Enum):
    unknown = 0
    public_transport = 1
    picnic_shelter = 2
    wather_shelter = 3
    weather_shelter = 6
    wildlife_hide = 7
    
    

class SupportType(enum.Enum):
    none = 0
    wall_mounted = 1
    ground = 2
    pole = 3
    billboard = 4
    tower = 5
    wall = 6
    
class OfficeType(enum.Enum):
    yes = -1
    employment_agency = 0
    insurance = 1
    physician = 2
    government = 3
    ngo = 4
    administrative = 5
    company = 6
    tax = 7
    religion = 8
    it = 9
    architect = 10
    estate_agent = 11
    therapist = 12
    telecommunication = 13
    lawyer = 14
    water_utility = 15
    educational_institution = 16
    coworking = 17
    translation = 18
    research = 19
    coworking_space = 20
    travel_agent = 21
    camping = 22
    money_lender = 23
    guide = 24
    financial = 25
    publisher = 26
    print_distribution = 27
    logistics = 28
    reception = 29
    

class ParkingLaneType(enum.Enum):
    no_parking = 0
    diagonal = 1
    no_stopping = 2
    parallel = 3
    perpendicular = 4
    inline = 5
    marked = 6
    on_street = 7
    yes = 8
    orthogonal = 9
    both = 10

