from .enums import LeisureType, SportType, AccessType, BarrierType, FenceType, IndoorType, InternetAccess
from . import Addressable
from ..validated_quantity import quantity

class Leisure(Addressable):
    type: LeisureType
    sport: SportType = None
    surface: str = None
    access: AccessType = None
    designation: str = None
    openfire: bool = None
    backrest: bool = None
    dogs_allowed: bool = None
    layer: int = None
    wikipedia: str = None
    phone: str = None
    operator: str = None
    hoops: int = None
    high_jump: bool = None
    pole_vault: bool = None
    long_jump: bool = None
    shot_put: bool = None
    covered: bool = None
    old_name: str = None
    barrier: BarrierType = None
    fence_type: FenceType = None
    wheelchair: bool = None
    entrance: bool = None
    baby: bool = None
    sorting_name: str = None
    fee: bool = None
    fenced: bool = None
    height: quantity("meter") = None
    lit: bool = None
    facebook: str = None
    small_boats: bool = None
    google_plus: str = None
    indoor: IndoorType = None
    alt_name_1: str = None
    start_date: str = None
    alt_name_2: str = None
    short_name: str = None
