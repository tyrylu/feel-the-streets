import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import BuildingType, OSMObjectType, WheelchairAccess, BicycleType

class TransportRelationship(enum.Enum):
    none = 0
    platform = 1
    tram_stop = 2
    platform_edge = 3
    
class Platform(Named):
    __tablename__ = "platforms"
    __mapper_args__ = {'polymorphic_identity': 'platform', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    train = Column(Boolean)
    bus = Column(Boolean)
    tram = Column(Boolean)
    railway = Column(IntEnum(TransportRelationship))
    shelter = Column(Boolean)
    bench = Column(Boolean)
    network = Column(UnicodeText)
    operator = Column(UnicodeText)
    surface = Column(UnicodeText)
    lit = Column(Boolean)
    wheelchair = Column(IntEnum(WheelchairAccess))
    covered = Column(Boolean)
    building = Column(IntEnum(BuildingType))
    bin = Column(Boolean)
    official_name = Column(UnicodeText)
    area = Column(Boolean)
    foot = Column(Boolean)
    layer = Column(Integer)
    trolleybus = Column(Boolean)
    tunnel = Column(Boolean)
    route_ref = Column(UnicodeText)
    bridge = Column(Boolean)
    tactile_paving = Column(Boolean)
    short_name = Column(UnicodeText)
    alt_name = Column(UnicodeText)
    fixme = Column(UnicodeText)
    note = Column(UnicodeText)
    description = Column(UnicodeText)
    level = Column(Integer)
    bicycle = Column(IntEnum(BicycleType))
    subway = Column(Boolean)
    width = Column(Integer)
    local_ref = Column(UnicodeText)
    indoor_level = Column(UnicodeText)

