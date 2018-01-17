from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Building
from .enums import OSMObjectType, GeneratorSource

class PowerPlant(Building):
    __tablename__ = "power_plants"
    __mapper_args__ = {'polymorphic_identity': 'power_plant', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("buildings.id"), primary_key=True)
    electricity_output = Column(UnicodeText)
    frequency= Column(Integer)
    plant_source = Column(IntEnum(GeneratorSource))

