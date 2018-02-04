import enum
from . import Named, Address
from .enums import BuildingType, LandType, OSMObjectType, WheelchairAccess

class CraftType(enum.Enum):
    carpenter = 0
    photographer = 1
    brewery = 2
    roofer = 3
    shoemaker = 4
    watchmaker = 5
    upholsterer = 6
    confectionery = 7
    dressmaker = 8
    key_cutter = 9
    electrician = 10
    handicraft = 11
    window_construction = 12
    plumber = 13
    tailor = 14
    jeweller = 15
    basket_maker = 16
    glaziery = 17
    photographic_laboratory = 18
    bookbinder = 19
    locksmith = 20
    stonemason = 21
    hvac = 22
    graphic_designer = 23
    designer = 24
    winery = 25
    caterer = 26
    gardener = 27

class Craft(Named):
    type: CraftType
    address: Address = None
    operator: str = None
    building: BuildingType = None
    outdoor_seating: bool = None
    opening_hours: str = None
    microbrewery: bool = None
    website: str = None
    landuse: LandType = None
    email: str = None
    phone: str = None
    level: int = None
    wheelchair: WheelchairAccess = None
    note: str = None
    internet_access: bool = None
    wikidata: str = None
    facebook: str = None
    fax: str = None
    layer: int = None
    databox: str = None
    start_date: int = None
    bitcoin_payment: bool = None