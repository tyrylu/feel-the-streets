import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import BuildingType, OSMObjectType

class TransportRelationship(enum.Enum):
    none = 0
    platform = 1
    tram_stop = 2

class Platform(Named):
    __tablename__ = "platforms"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'platform'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
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
    wheelchair = Column(Boolean)
    covered = Column(Boolean)
    building = Column(IntEnum(BuildingType))
    bin = Column(Boolean)
    official_name = Column(UnicodeText)