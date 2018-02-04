from . import Addressable
from .enums import BuildingType, InternetAccess, OfficeType

class Bank(Addressable):
    brand: str = None
    operator: str = None
    atm: bool = None
    wheelchair: bool = None
    drive_through: bool = None
    phone: str = None
    flats: int = None
    levels: int = None
    building_type: BuildingType = None
    start_date: str = None
    layer: int = None
    old_name: str = None
    wikipedia: str = None
    contactless_payment: bool = None
    office: OfficeType = None
