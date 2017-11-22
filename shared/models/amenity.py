import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, Boolean, UnicodeText
from ..sa_types import IntEnum
from . import Addressable
from .enums import Amenity, AccessType, SmokingType, HistoricType, BarrierType, OSMObjectType, LandType, LeisureType, SportType, WifiType, ParkingType, Surface, Location, WheelchairAccess

class CoverType(enum.Enum):
    no = 0
    yes = 1
    booth = 2

class PlaceType(enum.Enum):
    none = 0
    neighbourhood = 1
class ValvesType(enum.Enum):
    schrader = 0

class Amenity(Addressable):
    __tablename__ = "amenities"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["addressables.id", "addressables.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'amenity'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(Amenity))
    religion = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
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
    email = Column(UnicodeText)
    internet_access = Column(UnicodeText)
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
    description = Column(UnicodeText)
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
    level = Column(Integer)
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
    comment = Column(UnicodeText)
    voltage = Column(Integer) # Find out what they are