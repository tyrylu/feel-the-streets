import enum
from . import Named
from .enums import OSMObjectType, SurveillanceType, SurveillanceKind, SurveillanceZone, ManMade, LandType, Amenity, SupportType

class CameraMount(enum.Enum):
    ceiling = 0
    pole = 1
    wall = 2

class Authority(enum.Enum):
    defence = 0

class Surveillance(Named):
    type: SurveillanceType = None
    kind: SurveillanceKind = None
    zone: SurveillanceZone = None
    man_made: ManMade = None
    designation: str = None
    camera_mount: CameraMount = None
    fixme: str = None
    camera_direction: int = None
    height: int = None
    authority: Authority = None
    landuse: LandType = None
    level: int = None
    website: str = None
    surveillance_zone: SurveillanceZone = None
    amenity: Amenity = None
    support: SupportType = None
    covered: bool = None