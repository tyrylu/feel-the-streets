import enum
from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, BuildingType, BarrierType, GeneratorSource

class GeneratorType(enum.Enum):
    unknown = 0
    kaplan_turbine = 1
    solar_photovoltaic_panel = 2
    combined_cycle = 3
    
class PowerGenerator(Named):
    __tablename__ = "generators"
    __mapper_args__ = {'polymorphic_identity': 'generator', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    source = Column(IntEnum(GeneratorSource))
    type = Column(IntEnum(GeneratorType))
    electricity_output = Column(UnicodeText)
    method = Column(UnicodeText)
    building = Column(IntEnum(BuildingType))
    hot_water_output = Column(UnicodeText)
    frequency = Column(Integer)
    operator = Column(UnicodeText)
    start_date = Column(UnicodeText)
    steam_output = Column(UnicodeText)
    layer = Column(Integer)
    barrier = Column(IntEnum(BarrierType))
    note = Column(UnicodeText)

