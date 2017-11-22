import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
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
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'power_line'}
    id = Column(Integer, primary_key=True)
    type = Column(IntEnum(PowerLineType))
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    cables = Column(Integer)
    voltage = Column(Integer)
    wires = Column(IntEnum(WireType))
    frequency = Column(Integer)
    operator = Column(UnicodeText)
    note = Column(UnicodeText)
    route = Column(IntEnum(RouteType))
    layer = Column(Integer)
    location = Column(IntEnum(Location))
    
    
    
    @property
    def effective_width(self):
        return 0