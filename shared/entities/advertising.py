import enum
from . import Named
from .enums import AdvertisingType

class Advertising(Named):
    type: AdvertisingType
    height: int = None
    lit: bool = None
    direction: int = None
