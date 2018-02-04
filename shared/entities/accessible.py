from . import OSMEntity
from .enums import AccessType

class Accessible(OSMEntity):
    type: AccessType
    level: str = None
    door: AccessType = None