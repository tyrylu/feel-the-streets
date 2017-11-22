import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, WheelchairAccess, AccessType

class EntranceType(enum.Enum):
    main = 0
    yes = 1
    service = 2
    emergency = 3
    home = 4
    private = 5
    exit = 6
    garage = 7
    entrance = 8
    
    
class Entrance(Named):
    __tablename__ = "entrances"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'entrance'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(EntranceType), nullable=False)
    level = Column(Integer)
    bicycle = Column(Boolean)
    foot = Column(Boolean)
    wheelchair = Column(IntEnum(WheelchairAccess))
    horse = Column(Boolean)
    motorcar = Column(Boolean)
    motorcycle = Column(Boolean)
    access = Column(IntEnum(AccessType))