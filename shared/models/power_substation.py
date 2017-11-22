import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import BarrierType, OSMObjectType, RoofShape, BuildingType
from . import Named

class PowerSubstationType(enum.Enum):
    unspecified = 0
    distribution = 1
    industrial = 2
    minor_distribution = 3
    traction = 4
    transmission = 5
    

class Locate(enum.Enum):
    kiosk = 0
class PowerSubstation(Named):
    __tablename__ = "power_substations"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'power_substation'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(PowerSubstationType))
    location = Column(UnicodeText)
    voltage = Column(UnicodeText)
    frequency = Column(Integer)
    barrier = Column(IntEnum(BarrierType))
    building = Column(IntEnum(BuildingType))
    operator = Column(UnicodeText)
    building_levels = Column(Integer)
    roof_shape = Column(IntEnum(RoofShape))
    building_colour = Column(UnicodeText)
    height = Column(Integer)
    locate = Column(IntEnum(Locate))
    roof_colour = Column(UnicodeText)
    fixme = Column(UnicodeText)
    start_date = Column(UnicodeText)
    note = Column(UnicodeText)
    rating = Column(UnicodeText)
    