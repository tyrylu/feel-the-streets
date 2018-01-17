import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import BarrierType, OSMObjectType, RoofShape, BuildingType, FenceType, PowerSubstationType
from . import Named

class Locate(enum.Enum):
    kiosk = 0

class PowerSubstation(Named):
    __tablename__ = "power_substations"
    __mapper_args__ = {'polymorphic_identity': 'power_substation', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
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
    roof_levels = Column(Integer)
    gas_insulated = Column(Boolean)
    fence_type = Column(IntEnum(FenceType))
    access = Column(Boolean)
    low_voltage = Column(Integer)
    wikidata = Column(UnicodeText)
    description = Column(UnicodeText)

