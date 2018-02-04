import enum
from . import OSMEntity
from .enums import AdvertisingType

class Advertising(OSMEntity):
    type: AdvertisingType
    height: int = None
    lit: bool = None
    direction: int = None
    name: str = None