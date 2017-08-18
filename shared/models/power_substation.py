import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from .enums import BarrierType
from . import Named

class PowerSubstationType(enum.Enum):
    unspecified = 0
    distribution = 1
    industrial = 2
    minor_distribution = 3
    traction = 4

class PowerSubstation(Named):
    __tablename__ = "power_substations"
    __mapper_args__ = {'polymorphic_identity': 'power_substation'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(PowerSubstationType))
    location = Column(UnicodeText)
    voltage = Column(UnicodeText)
    frequency = Column(Integer)
    barrier = Column(Enum(BarrierType))
    building = Column(Boolean)