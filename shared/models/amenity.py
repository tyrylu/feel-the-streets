import enum
from sqlalchemy import Column, ForeignKey, Integer, Boolean, UnicodeText
from ..sa_types import IntEnum
from . import Addressable
from .enums import Amenity, AccessType, SmokingType, HistoricType, BarrierType, OSMObjectType, LandType, LeisureType, SportType, WifiType, ParkingType, Surface, Location, WheelchairAccess, PlaceType, ToiletsDisposal, FastFoodType, ManMade, DiplomacyRelation, DietType, FenceType

class CoverType(enum.Enum):
    no = 0
    yes = 1
    booth = 2

class ValvesType(enum.Enum):
    schrader = 0

class Genre(enum.Enum):
    black_light_theatre = 0
    cabaret = 1

class StudioType(enum.Enum):
    audio = 0
    video_editing = 1

class Amenity(Addressable):
    __tablename__ = "amenities"
    __mapper_args__ = {'polymorphic_identity': 'amenity', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    type = Column(IntEnum(Amenity))
    religion = Column(UnicodeText)
    operator = Column(UnicodeText)
    cuisine = Column(UnicodeText)
    phone = Column(UnicodeText)
    official_name = Column(UnicodeText)
    community_centre_for = Column(UnicodeText)
    takeaway = Column(UnicodeText)
    vending = Column(UnicodeText)
    outdoor_seating = Column(Boolean)
    access = Column(IntEnum(AccessType))
    smoking = Column(IntEnum(SmokingType))
    amenity_1 = Column(IntEnum(Amenity))
    drive_through = Column(Boolean)
    backrest = Column(Boolean)
    material = Column(UnicodeText)
    place_type = Column(IntEnum(PlaceType))
    seats = Column(Integer)
    unisex = Column(Boolean)
    covered = Column(IntEnum(CoverType))
    wheelchair = Column(IntEnum(WheelchairAccess))
    facebook = Column(UnicodeText)
    shelter = Column(Boolean)
    hide = Column(Boolean)
    url = Column(UnicodeText)
    denomination = Column(UnicodeText)
    vegetarian_diet = Column(Boolean)
    historic = Column(IntEnum(HistoricType))
    dispensing = Column(Boolean)
    barrier = Column(IntEnum(BarrierType))
    capacity = Column(Integer)
    emergency = Column(Boolean)
    old_name = Column(UnicodeText)
    brewery = Column(UnicodeText)
    delivery = Column(Boolean)
    postal_code = Column(Integer)
    open_air = Column(Boolean)
    short_name = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    landuse = Column(IntEnum(LandType))
    leisure = Column(IntEnum(LeisureType))
    start_date = Column(UnicodeText)
    sport = Column(IntEnum(SportType))
    wifi = Column(IntEnum(WifiType))
    bottle = Column(Boolean)
    fee = Column(Boolean)
    lockable = Column(Boolean)
    colour = Column(UnicodeText)
    height = Column(Integer)
    lit = Column(Boolean)
    parking = Column(IntEnum(ParkingType))
    surface = Column(IntEnum(Surface))
    todo = Column(UnicodeText)
    drinking_water = Column(Boolean)
    cargo = Column(UnicodeText)
    charge = Column(UnicodeText)
    int_name = Column(UnicodeText)
    internet_access_fee = Column(Boolean)
    internet_access_ssid = Column(UnicodeText)
    designation = Column(UnicodeText)
    location = Column(IntEnum(Location))
    valves = Column(IntEnum(ValvesType))
    supervised = Column(Boolean)
    car = Column(Boolean)
    car_capacity = Column(Integer)
    direction = Column(Integer)
    nfc_authentication = Column(Boolean)
    layer = Column(Integer)
    dog = Column(Boolean)
    female = Column(Boolean)
    male = Column(Boolean)
    voltage = Column(Integer)
    toilets_disposal = Column(IntEnum(ToiletsDisposal))
    country = Column(UnicodeText)
    schuko_socket = Column(Integer)
    schuko_socket_voltage = Column(UnicodeText)
    type2_socket_voltage = Column(UnicodeText)
    waste = Column(UnicodeText)
    fast_food = Column(IntEnum(FastFoodType))
    man_made = Column(IntEnum(ManMade))
    wheelchair_toilets = Column(Boolean)
    fax = Column(UnicodeText)
    diplomatic = Column(IntEnum(DiplomacyRelation))
    automated = Column(Boolean)
    toilets = Column(Boolean)
    vegan_diet = Column(IntEnum(DietType))
    indoor_seating = Column(Boolean)
    short_name_en = Column(UnicodeText)
    fence_type = Column(IntEnum(FenceType))
    beer = Column(UnicodeText)
    atm = Column(Boolean)
    chademo_socket = Column(Integer)
    community = Column(UnicodeText)
    gambling = Column(Boolean)
    disused = Column(Boolean)
    foot = Column(Boolean)
    genre = Column(IntEnum(Genre))
    beer_garden = Column(Boolean)
    chademo_socket_power = Column(UnicodeText)
    studio = Column(IntEnum(StudioType))
    wine = Column(Boolean)
    sorting_name = Column(UnicodeText)
    room = Column(IntEnum(Amenity))
    type2_socket = Column(Integer)
    schuko_socket_current = Column(UnicodeText)
    # Find out what they are
