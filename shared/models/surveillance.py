import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Entity
from .enums import OSMObjectType, SurveillanceType, SurveillanceKind, SurveillanceZone, ManMade, LandType, Amenity, SupportType

class CameraMount(enum.Enum):
    ceiling = 0
    pole = 1
    wall = 2

class Authority(enum.Enum):
    defence = 0

class Surveillance(Entity):
    __tablename__ = "surveillances"
    __mapper_args__ = {'polymorphic_identity': 'surveillance', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(IntEnum(SurveillanceType))
    kind = Column(IntEnum(SurveillanceKind))
    zone = Column(IntEnum(SurveillanceZone))
    man_made = Column(IntEnum(ManMade))
    designation = Column(UnicodeText)
    camera_mount = Column(IntEnum(CameraMount))
    fixme = Column(UnicodeText)
    camera_direction = Column(Integer)
    height = Column(Integer)
    authority = Column(IntEnum(Authority))
    landuse = Column(IntEnum(LandType))
    level = Column(Integer)
    website = Column(UnicodeText)
    name = Column(UnicodeText)
    surveillance_zone = Column(IntEnum(SurveillanceZone))
    amenity = Column(IntEnum(Amenity))
    support = Column(IntEnum(SupportType))
    covered = Column(Boolean)
