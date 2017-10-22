import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

class GeneratorSource(enum.Enum):
    unknown = 0
    hydro = 1
    solar = 2
    solar_photovoltaic_panel = 3

class GeneratorType(enum.Enum):
    unknown = 0
    kaplan_turbine = 1
    solar_photovoltaic_panel = 2
    combined_cycle = 3
    

class PowerGenerator(Named):
    __tablename__ = "generators"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'generator'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    source = Column(IntEnum(GeneratorSource))
    type = Column(IntEnum(GeneratorType))
    electricity_output = Column(UnicodeText)
    method = Column(UnicodeText)