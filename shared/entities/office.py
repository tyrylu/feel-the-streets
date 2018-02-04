import enum
from . import Addressable
from .enums import SmokingType, LandType, BarrierType, WheelchairAccess, RoofShape, RoofMaterial, IndoorType, Amenity, InternetAccess, OfficeType

class Function(enum.Enum):
    retail = 0
    headquarters = 1

class AuthorityType(enum.Enum):
    finance = 0
    culture = 1
    interior = 2
    yes = 3

class GovernmentRelation(enum.Enum):
    tax = 1
    transportation = 2
    cadaster = 3
    ministry = 4
    archive = 5
    
class LawyerType(enum.Enum):
    notary = 0

class Office(Addressable):
    type: OfficeType
    phone: str = None
    smoking: SmokingType = None
    official_name: str = None
    levels: int = None
    government: GovernmentRelation = None
    landuse: LandType = None
    short_name: str = None
    wikipedia: str = None
    barrier: BarrierType = None
    phone: str = None
    denomination: str = None
    religion: str = None
    wheelchair: WheelchairAccess = None
    operator: str = None
    brand: str = None
    bitcoin_payment: bool = None
    authority: AuthorityType = None
    old_name: str = None
    roof_material: RoofMaterial = None
    roof_shape: RoofShape = None
    roof_height: int = None
    roof_colour: str = None
    flats: int = None
    function: Function = None
    indoor: IndoorType = None
    amenity: Amenity = None
    fax: str = None
    lawyer: LawyerType = None
    phone_1: str = None
    facebook: str = None
    start_date: str = None
    designation: str = None
    description_en: str = None
