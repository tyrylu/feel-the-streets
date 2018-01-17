import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, RouteType, Location

class WireType(enum.Enum):
    unknown = 0
    single = 1
    double = 2
    triple = 3

class PowerLineType(enum.Enum):
    bay = 0
    busbar = 1
    route = 2
    
class PowerLine(Named):
    __tablename__ = "power_lines"
    __mapper_args__ = {'polymorphic_identity': 'power_line', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(PowerLineType))
    cables = Column(Integer)
    voltage = Column(Integer)
    wires = Column(IntEnum(WireType))
    frequency = Column(Integer)
    operator = Column(UnicodeText)
    note = Column(UnicodeText)
    route = Column(IntEnum(RouteType))
    layer = Column(Integer)
    location = Column(IntEnum(Location))
    circuits = Column(Integer)
    line_colour = Column(UnicodeText)
    colour = Column(UnicodeText)
    description = Column(UnicodeText)
    complete = Column(Boolean)
    fixme = Column(UnicodeText)



    @property
    def effective_width(self):
        return 0
