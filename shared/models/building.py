import enum
from sqlalchemy import Column, ForeignKey, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum, DimensionalFloat
from .enums import LeisureType, Amenity, ManMade, SmokingType, TourismType, SportType, InfoType, HistoricType, RoofShape, Location, AccessType, OSMObjectType, IndustrialType, LandType, BuildingPartType, BarrierType, RoofOrientation, ConstructionType, ReservationType, WifiType, WheelchairAccess, RoofMaterial, IndoorType, FenceType, Surface, ResidentialType, GardenType, EmergencyType, Material, ArtWorkType, AdvertisingType, BuildingType, SurveillanceType, ToiletsDisposal, FastFoodType, DiplomacyRelation, DietType
from . import Addressable

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
    __tablename__ = "buildings"
    __mapper_args__ = {'polymorphic_identity': 'building', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    levels = Column(Integer)
    flats = Column(Integer)
    amenity = Column(IntEnum(Amenity))
    religion = Column(UnicodeText)
    official_name = Column(UnicodeText)
    capacity = Column(Integer)
    start_date = Column(UnicodeText)
    denomination = Column(UnicodeText)
    layer = Column(Integer)
    takeaway = Column(IntEnum(TakeAway))
    smoking = Column(IntEnum(SmokingType))
    delivery = Column(Boolean)
    emergency = Column(IntEnum(EmergencyType))
    leisure_type = Column(IntEnum(LeisureType))
    tourism_type = Column(IntEnum(TourismType))
    man_made = Column(IntEnum(ManMade))
    operator = Column(UnicodeText)
    industrial_type = Column(IntEnum(IndustrialType))
    roof_height = Column(Float)
    roof_shape = Column(IntEnum(RoofShape))
    height = Column(DimensionalFloat("meter"))
    internet_access_fee = Column(Boolean)
    sport = Column(IntEnum(SportType))
    covered = Column(Boolean)
    wikipedia = Column(UnicodeText)
    old_name = Column(UnicodeText)
    short_name = Column(UnicodeText)
    information_type = Column(IntEnum(InfoType))
    location = Column(IntEnum(Location))
    product = Column(UnicodeText)
    dispensing = Column(Boolean)
    colour = Column(UnicodeText)
    community_centre_for = Column(UnicodeText)
    historic_type = Column(IntEnum(HistoricType))
    cuisine = Column(UnicodeText)
    phone = Column(UnicodeText)
    outdoor_seating = Column(Boolean)
    brewery = Column(UnicodeText)
    vegetarian_diet = Column(IntEnum(DietType))
    heritage = Column(Integer)
    heritage_operator = Column(UnicodeText)
    access = Column(IntEnum(AccessType))
    architect = Column(UnicodeText)
    designation = Column(UnicodeText)
    abandoned = Column(Boolean)
    wheelchair = Column(IntEnum(WheelchairAccess))
    landuse = Column(IntEnum(LandType))
    roof_levels = Column(Integer)
    roof_material = Column(IntEnum(RoofMaterial))
    part = Column(IntEnum(BuildingPartType))
    service_times = Column(UnicodeText)
    image = Column(UnicodeText)
    disused = Column(Boolean)
    barrier = Column(IntEnum(BarrierType))
    underground_levels = Column(Integer)
    roof_angle = Column(Integer)
    roof_orientation = Column(IntEnum(RoofOrientation))
    min_level = Column(Integer)
    cladding = Column(IntEnum(Cladding))
    material = Column(IntEnum(Material))
    brand = Column(UnicodeText)
    stars = Column(Integer)
    fee = Column(Boolean)
    date = Column(UnicodeText)
    int_name = Column(UnicodeText)
    fax = Column(UnicodeText)
    use = Column(IntEnum(BuildingUsage))
    roof_colour = Column(UnicodeText)
    wheelchair_description = Column(UnicodeText)
    construction = Column(IntEnum(ConstructionType))
    self_service = Column(Boolean)
    microbrewery = Column(Boolean)
    ruins = Column(Boolean)
    wheelchair_toilets = Column(IntEnum(AccessType))
    wifi = Column(IntEnum(WifiType))
    opening_hours_url = Column(UnicodeText)
    reservation = Column(IntEnum(ReservationType))
    visa_payment = Column(Boolean)
    visa_debit_payment = Column(Boolean)
    visa_electron_payment = Column(Boolean)
    healthcare_speciality = Column(UnicodeText)
    # Find out why it appears there
    sorting_name = Column(UnicodeText)
    alt_name_1 = Column(UnicodeText)
    alt_name_2 = Column(UnicodeText)
    end_date = Column(UnicodeText)
    # Make it a date
    cvut_id = Column(UnicodeText)
    description_en = Column(UnicodeText)
    internet_access_ssid = Column(UnicodeText)
    min_height = Column(Float)
    max_level = Column(Integer)
    drive_through = Column(Boolean)
    cash_payment = Column(Boolean)
    facebook = Column(UnicodeText)
    diplomatic = Column(IntEnum(DiplomacyRelation))
    note_en = Column(UnicodeText)
    bitcoin_payment = Column(Boolean)
    artist_name = Column(UnicodeText)
    rooms = Column(Integer)
    google_plus = Column(UnicodeText)
    twitter = Column(UnicodeText)
    fence_type = Column(IntEnum(FenceType))
    toilets_disposal = Column(IntEnum(ToiletsDisposal))
    toilets = Column(Boolean)
    bridge = Column(Boolean)
    maestro_payment = Column(Boolean)
    mastercard_payment = Column(Boolean)
    notes_payment = Column(Boolean)
    male = Column(Boolean)
    female = Column(Boolean)
    beer = Column(UnicodeText)
    surface = Column(IntEnum(Surface))
    todo = Column(UnicodeText)
    indoor = Column(IntEnum(IndoorType))
    automated = Column(Boolean)
    vegan_diet = Column(IntEnum(DietType))
    fast_food = Column(IntEnum(FastFoodType))
    # Separate entity?
    credit_cards_payment = Column(Boolean)
    debit_cards_payment = Column(Boolean)
    roof_slope_direction = Column(Float)
    roof_direction = Column(UnicodeText)
    bridge_support = Column(IntEnum(BridgeSupport))
    room = Column(IntEnum(Amenity))
    floating = Column(Boolean)
    memorial = Column(UnicodeText)
    gluten_free_diet = Column(Boolean)
    ethnicity = Column(IntEnum(Ethnicity))
    residential = Column(IntEnum(ResidentialType))
    fenced = Column(Boolean)
    disused_man_made = Column(IntEnum(ManMade))
    vertical_part = Column(Boolean)
    mooring = Column(IntEnum(AccessType))
    seamark_type = Column(IntEnum(SeaMarkType))
    flat = Column(IntEnum(Surface))
    raw_diet = Column(Boolean)
    en_wheelchair_description = Column(UnicodeText)
    electronic_purses_payment = Column(Boolean)
    kids_area = Column(Boolean)
    beer_1 = Column(UnicodeText)
    country = Column(UnicodeText)
    garden_type = Column(IntEnum(GardenType))
    meal_voucher_payment = Column(UnicodeText)
    artwork_type = Column(IntEnum(ArtWorkType))
    architecture = Column(IntEnum(Architecture))
    currency_czk = Column(Boolean)
    real_ale = Column(Boolean)
    camp_site = Column(IntEnum(CampSiteRelation))
    advertising = Column(IntEnum(AdvertisingType))
    american_express_payment = Column(Boolean)
    cryptocurrencies_payment = Column(Boolean)
    entrance = Column(Boolean)
    name_1 = Column(UnicodeText)
    reg_name = Column(UnicodeText)
    secondary_use = Column(UnicodeText)
    building_1 = Column(IntEnum(BuildingType))
    inscription = Column(UnicodeText)
    surveillance = Column(IntEnum(SurveillanceType))
    roof_access = Column(IntEnum(AccessType))
    hei = Column(UnicodeText)
    owner = Column(UnicodeText)
    meal_vouchers_payment = Column(Boolean)
    amenity_1 = Column(IntEnum(Amenity))
    education = Column(IntEnum(EducationType))

