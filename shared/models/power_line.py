import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

class WireType(enum.Enum):
    unknown = 0
    single = 1
    double = 2
    triple = 3

class PowerLine(Named):
    __tablename__ = "power_lines"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'power_line'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    cables = Column(Integer)
    voltage = Column(Integer)
    wires = Column(IntEnum(WireType))
    frequency = Column(Integer)
    operator = Column(UnicodeText)
    
    @property
    def effective_width(self):
        return 0