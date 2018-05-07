from .enums import BuildingType, ShopType, WheelchairAccess, RoofShape, AccessType
from . import Named
from . import Address

class Fuel(Named):
    operator: str = None
    brand: str = None
    opening_hours: str = None
    internet_access: str = None
    internet_access_paid: str = None
    shop: ShopType = None
    phone: str = None
    address: Address = None
    building_type: BuildingType = None
    levels: int = None
    note: str = None
    start_date: str = None
    website: str = None
    wheelchair: WheelchairAccess = None
    email: str = None
    roof_shape: RoofShape = None
    roof_colour: str = None
    access: AccessType = None