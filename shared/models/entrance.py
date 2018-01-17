import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, WheelchairAccess, AccessType, EntranceType, MilitaryType

class DoorType(enum.Enum):
    yes = 0
    overhead = 1
    hinged = 2
    rotating = 3

class Entrance(Named):
    __tablename__ = "entrances"
    __mapper_args__ = {'polymorphic_identity': 'entrance', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(EntranceType), nullable=False)
    level = Column(Integer)
    bicycle = Column(Boolean)
    foot = Column(Boolean)
    wheelchair = Column(IntEnum(WheelchairAccess))
    horse = Column(Boolean)
    motorcar = Column(Boolean)
    motorcycle = Column(Boolean)
    access = Column(IntEnum(AccessType))
    door = Column(IntEnum(DoorType))
    note = Column(UnicodeText)
    description = Column(UnicodeText)
    military = Column(IntEnum(MilitaryType))
    fixme = Column(UnicodeText)
