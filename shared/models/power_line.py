import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from . import Named

class WireType(enum.Enum):
    unknown = 0
    single = 1
    double = 2
    triple = 3

class PowerLine(Named):
    __tablename__ = "power_lines"
    __mapper_args__ = {'polymorphic_identity': 'power_line'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    cables = Column(Integer)
    voltage = Column(Integer)
    wires = Column(Enum(WireType))
    frequency = Column(Integer)
    operator = Column(UnicodeText)
    
    @property
    def effective_width(self):
        return 0