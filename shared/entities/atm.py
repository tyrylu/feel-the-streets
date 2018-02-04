from . import Addressable
from .enums import WheelchairAccess, Location, AccessType

class ATM(Addressable):
    operator: str = None
    contact_website: str = None
    fee: str = None
    drive_through: bool = None
    phone: str = None
    wheelchair: WheelchairAccess = None
    brand: str = None
    layer: int = None
    location: Location = None
    cash_in: bool = None
    bitcoin: bool = None
    access: AccessType = None
