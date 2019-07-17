import enum
from . import Addressable
from .enums import Amenity, AccessType, SmokingType, HistoricType, BarrierType, LandType, LeisureType, SportType, WifiType, ParkingType, Surface, Location, WheelchairAccess, PlaceType, ToiletsDisposal, FastFoodType, ManMade, DiplomacyRelation, DietType, FenceType
from shared.humanization_utils import underscored_to_words

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
    type: Amenity = None
    religion: str = None
    operator: str = None
    cuisine: str = None
    phone: str = None
    official_name: str = None
    community_centre_for: str = None
    takeaway: str = None
    vending: str = None
    outdoor_seating: bool = None
    access: AccessType = None
    smoking: SmokingType = None
    amenity_1: Amenity = None
    drive_through: bool = None
    backrest: bool = None
    material: str = None
    place_type: PlaceType = None
    seats: int = None
    unisex: bool = None
    covered: CoverType = None
    wheelchair: WheelchairAccess = None
    facebook: str = None
    shelter: bool = None
    hide: bool = None
    url: str = None
    denomination: str = None
    vegetarian_diet: bool = None
    historic: HistoricType = None
    dispensing: bool = None
    barrier: BarrierType = None
    capacity: int = None
    emergency: bool = None
    old_name: str = None
    brewery: str = None
    delivery: bool = None
    postal_code: int = None
    open_air: bool = None
    short_name: str = None
    wikipedia: str = None
    landuse: LandType = None
    leisure: LeisureType = None
    start_date: str = None
    sport: SportType = None
    wifi: WifiType = None
    bottle: bool = None
    fee: bool = None
    lockable: bool = None
    colour: str = None
    height: int = None
    lit: bool = None
    parking: ParkingType = None
    surface: Surface = None
    todo: str = None
    drinking_water: bool = None
    cargo: str = None
    charge: str = None
    int_name: str = None
    internet_access_fee: bool = None
    internet_access_ssid: str = None
    designation: str = None
    location: Location = None
    valves: ValvesType = None
    supervised: bool = None
    car: bool = None
    car_capacity: int = None
    direction: int = None
    nfc_authentication: bool = None
    layer: int = None
    dog: bool = None
    female: bool = None
    male: bool = None
    voltage: int = None
    toilets_disposal: ToiletsDisposal = None
    country: str = None
    schuko_socket: int = None
    schuko_socket_voltage: str = None
    type2_socket_voltage: str = None
    waste: str = None
    fast_food: FastFoodType = None
    man_made: ManMade = None
    wheelchair_toilets: bool = None
    fax: str = None
    diplomatic: DiplomacyRelation = None
    automated: bool = None
    toilets: bool = None
    vegan_diet: DietType = None
    indoor_seating: bool = None
    short_name_en: str = None
    fence_type: FenceType = None
    beer: str = None
    atm: bool = None
    chademo_socket: int = None
    community: str = None
    gambling: bool = None
    disused: bool = None
    foot: bool = None
    genre: Genre = None
    beer_garden: bool = None
    chademo_socket_power: str = None
    studio: StudioType = None
    wine: bool = None
    sorting_name: str = None
    room: Amenity = None
    type2_socket: int = None
    schuko_socket_current: str = None
    # Find out what they are

    def __str__(self):
        retval = super().__str__()
        if self.type:
            retval += " - {}".format(underscored_to_words(self.type.name))
        return retval