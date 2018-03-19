import enum
from .enums import LeisureType, Amenity, ManMade, SmokingType, TourismType, SportType, InfoType, HistoricType, RoofShape, Location, AccessType, IndustrialType, LandType, BuildingPartType, BarrierType, RoofOrientation, ConstructionType, ReservationType, WifiType, WheelchairAccess, RoofMaterial, IndoorType, FenceType, Surface, ResidentialType, GardenType, EmergencyType, Material, ArtWorkType, AdvertisingType, BuildingType, SurveillanceType, ToiletsDisposal, FastFoodType, DiplomacyRelation, DietType
from . import Addressable
from ..validated_quantity import quantity

class RUIANType(enum.Enum):
    industrial_object = 1
    farm_dwelling = 2
    residential_object = 3
    building_of_forest_management = 4
    building_of_civic_management = 5
    apartment_house = 6
    family_house = 7
    building_for_family_recreation = 8
    building_for_gathering_of_people = 9
    commercial_building = 10
    building_for_accomodation = 11
    warehouse_building = 12
    agricultural_building = 13
    administrative_building = 14
    building_of_civic_infrastructure = 15
    building_of_technical_infrastructure = 16
    building_for_transportation = 17
    garage = 18
    other_building = 19
    multipurpose_building = 20
    greenhouse = 21
    dam_of_the_artificial_lake = 22
    dam_blocking_water_way_or_walley = 23
    flood_protection_dam = 24
    dam_surrounding_artificial_lake = 25
    weir = 26
    building_for_water_transportation = 27
    water_power_plant = 28
    sludge_lagoon = 29




class TakeAway(enum.Enum):
    no = 0
    yes = 1
    only = 2

class BuildingUsage(enum.Enum):
    residential = 0
    commercial = 1
    shop = 2
    garages = 3

class Cladding(enum.Enum):
    glass = 0

class BridgeSupport(enum.Enum):
    pier = 0

class Ethnicity(enum.Enum):
    czech = 0

class SeaMarkType(enum.Enum):
    anchor_berth = 0

class Architecture(enum.Enum):
    romanesque = 0
    modern = 1

class CampSiteRelation(enum.Enum):
    reception = 0

class EducationType(enum.Enum):
    music = 0

class Building(Addressable):
    levels: int = None
    flats: int = None
    amenity: Amenity = None
    religion: str = None
    official_name: str = None
    capacity: int = None
    start_date: str = None
    denomination: str = None
    layer: int = None
    takeaway: TakeAway = None
    smoking: SmokingType = None
    delivery: bool = None
    emergency: EmergencyType = None
    leisure_type: LeisureType = None
    tourism_type: TourismType = None
    man_made: ManMade = None
    operator: str = None
    industrial_type: IndustrialType = None
    roof_height: float = None
    roof_shape: RoofShape = None
    height: quantity("meter") = None
    internet_access_fee: bool = None
    sport: SportType = None
    covered: bool = None
    wikipedia: str = None
    old_name: str = None
    short_name: str = None
    information_type: InfoType = None
    location: Location = None
    product: str = None
    dispensing: bool = None
    colour: str = None
    community_centre_for: str = None
    historic_type: HistoricType = None
    cuisine: str = None
    phone: str = None
    outdoor_seating: bool = None
    brewery: str = None
    vegetarian_diet: DietType = None
    heritage: int = None
    heritage_operator: str = None
    access: AccessType = None
    architect: str = None
    designation: str = None
    abandoned: bool = None
    wheelchair: WheelchairAccess = None
    landuse: LandType = None
    roof_levels: int = None
    roof_material: RoofMaterial = None
    part: BuildingPartType = None
    service_times: str = None
    image: str = None
    disused: bool = None
    barrier: BarrierType = None
    underground_levels: int = None
    roof_angle: int = None
    roof_orientation: RoofOrientation = None
    min_level: int = None
    cladding: Cladding = None
    material: Material = None
    brand: str = None
    stars: int = None
    fee: bool = None
    date: str = None
    int_name: str = None
    fax: str = None
    use: BuildingUsage = None
    roof_colour: str = None
    wheelchair_description: str = None
    construction: ConstructionType = None
    self_service: bool = None
    microbrewery: bool = None
    ruins: bool = None
    wheelchair_toilets: AccessType = None
    wifi: WifiType = None
    opening_hours_url: str = None
    reservation: ReservationType = None
    visa_payment: bool = None
    visa_debit_payment: bool = None
    visa_electron_payment: bool = None
    healthcare_speciality: str = None
    # Find out why it appears there
    sorting_name: str = None
    alt_name_1: str = None
    alt_name_2: str = None
    end_date: str = None
    # Make it a date
    cvut_id: str = None
    description_en: str = None
    internet_access_ssid: str = None
    min_height: float = None
    max_level: int = None
    drive_through: bool = None
    cash_payment: bool = None
    facebook: str = None
    diplomatic: DiplomacyRelation = None
    note_en: str = None
    bitcoin_payment: bool = None
    artist_name: str = None
    rooms: int = None
    google_plus: str = None
    twitter: str = None
    fence_type: FenceType = None
    toilets_disposal: ToiletsDisposal = None
    toilets: bool = None
    bridge: bool = None
    maestro_payment: bool = None
    mastercard_payment: bool = None
    notes_payment: bool = None
    male: bool = None
    female: bool = None
    beer: str = None
    surface: Surface = None
    todo: str = None
    indoor: IndoorType = None
    automated: bool = None
    vegan_diet: DietType = None
    fast_food: FastFoodType = None
    # Separate entity?
    credit_cards_payment: bool = None
    debit_cards_payment: bool = None
    roof_slope_direction: float = None
    roof_direction: str = None
    bridge_support: BridgeSupport = None
    room: Amenity = None
    floating: bool = None
    memorial: str = None
    gluten_free_diet: bool = None
    ethnicity: Ethnicity = None
    residential: ResidentialType = None
    fenced: bool = None
    disused_man_made: ManMade = None
    vertical_part: bool = None
    mooring: AccessType = None
    seamark_type: SeaMarkType = None
    flat: Surface = None
    raw_diet: bool = None
    en_wheelchair_description: str = None
    electronic_purses_payment: bool = None
    kids_area: bool = None
    beer_1: str = None
    country: str = None
    garden_type: GardenType = None
    meal_voucher_payment: str = None
    artwork_type: ArtWorkType = None
    architecture: Architecture = None
    currency_czk: bool = None
    real_ale: bool = None
    camp_site: CampSiteRelation = None
    advertising: AdvertisingType = None
    american_express_payment: bool = None
    cryptocurrencies_payment: bool = None
    entrance: bool = None
    name_1: str = None
    reg_name: str = None
    secondary_use: str = None
    building_1: BuildingType = None
    inscription: str = None
    surveillance: SurveillanceType = None
    roof_access: AccessType = None
    hei: str = None
    owner: str = None
    meal_vouchers_payment: bool = None
    amenity_1: Amenity = None
    education: EducationType = None
    ruian_type: RUIANType = None
    ruian_building_ref: int = None
