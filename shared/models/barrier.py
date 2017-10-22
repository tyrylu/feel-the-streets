import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import BarrierType, AccessType, ManMade, OSMObjectType
from . import Named

class BollardType(enum.Enum):
    rising = 1
    removable = 2
    yes = 3
    irremovable = 4
    
class Barrier(Named):
    __tablename__ = "barriers"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'barrier'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(BarrierType), nullable=False)
    foot = Column(Boolean)
    bicycle = Column(Boolean)
    vehicle = Column(Boolean)
    horse = Column(Boolean)
    access = Column(IntEnum(AccessType))
    entrance = Column(UnicodeText)
    motor_vehicle = Column(UnicodeText)
    note = Column(UnicodeText)
    maxwidth = Column(Integer)
    fence_type = Column(UnicodeText)
    height = Column(Float)
    material = Column(UnicodeText)
    motorcar = Column(Boolean)
    motorcycle = Column(Boolean)
    toll = Column(Boolean)
    operator = Column(UnicodeText)
    toll_hgv = Column(Boolean)
    opening_hours = Column(UnicodeText)
    bollard = Column(IntEnum(BollardType))
    destination = Column(Boolean)
    noexit = Column(Boolean)
    ticks = Column(Integer)
    man_made = Column(IntEnum(ManMade))
    description = Column(UnicodeText)
    fixme = Column(UnicodeText)
    two_sided = Column(Boolean)
    historic = Column(Boolean)
    