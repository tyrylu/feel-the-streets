import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum, DimensionalFloat
from .enums import LeisureType, Amenity, ManMade, SmokingType, TourismType, SportType, InfoType, HistoricType, RoofShape, Location, AccessType, OSMObjectType, IndustrialType, LandType, BuildingPartType, BarrierType, RoofOrientation, ConstructionType, ReservationType, WifiType, WheelchairAccess, RoofMaterial, IndoorType, FenceType, Surface
from . import Addressable

class DietType(enum.Enum):
    no = 0
    yes = 1
    only = 2

class FastFoodType(enum.Enum):
    yes = 0
    cafeteria = 1

class ToiletsDisposal(enum.Enum):
    flush = 0
class DiplomacyRelation(enum.Enum):
    ambassadors_residence = 0
    embassy = 1

class TakeAway(enum.Enum):
    no = 0
    yes = 1
    only = 2

class BuildingUsage(enum.Enum):
    residential = 0
    commercial = 1

class EmergencyType(enum.Enum):
    no = 0
    yes = 1
    ambulance_station = 2
class Cladding(enum.Enum):
    glass = 0
class Material(enum.Enum):
    glass = 0
    steel = 1

class Building(Addressable):
    __tablename__ = "buildings"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["addressables.id", "addressables.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'building'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    levels = Column(Integer)
    flats = Column(Integer)
    opening_hours = Column(UnicodeText)
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
    wikidata = Column(UnicodeText)
    internet_access = Column(UnicodeText)
    sport = Column(IntEnum(SportType))
    covered = Column(Boolean)
    alt_name = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    old_name = Column(UnicodeText)
    short_name = Column(UnicodeText)
    information_type = Column(IntEnum(InfoType))
    description = Column(UnicodeText)
    location = Column(IntEnum(Location))
    product = Column(UnicodeText)
    dispensing = Column(Boolean)
    colour = Column(UnicodeText)
    community_centre_for = Column(UnicodeText)
    historic_type = Column(IntEnum(HistoricType))
    cuisine = Column(UnicodeText)
    phone = Column(UnicodeText)
    email = Column(UnicodeText)
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
    level = Column(Integer)
    landuse = Column(IntEnum(LandType))
    roof_levels = Column(Integer)
    roof_material = Column(IntEnum(RoofMaterial))
    part = Column(IntEnum(BuildingPartType))
    loc_name = Column(UnicodeText)
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
    comment = Column(UnicodeText)
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
    healthcare_speciality = Column(UnicodeText) # Find out why it appears there
    sorting_name = Column(UnicodeText)
    alt_name_1 = Column(UnicodeText)
    alt_name_2 = Column(UnicodeText)
    end_date = Column(UnicodeText) # Make it a date
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
    fast_food = Column(IntEnum(FastFoodType)) # Separate entity?
    credit_cards_payment = Column(Boolean)
    debit_cards_payment = Column(Boolean)
    