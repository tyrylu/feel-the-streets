import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from . import Named

class GeneratorSource(enum.Enum):
    unknown = 0
    hydro = 1
    solar = 2
    solar_photovoltaic_panel = 3

class GeneratorType(enum.Enum):
    unknown = 0
    kaplan_turbine = 1
    solar_photovoltaic_panel = 2

class PowerGenerator(Named):
    __tablename__ = "generators"
    __mapper_args__ = {'polymorphic_identity': 'generator'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    source = Column(Enum(GeneratorSource))
    type = Column(Enum(GeneratorType))
    electricity_output = Column(UnicodeText)
    method = Column(UnicodeText)