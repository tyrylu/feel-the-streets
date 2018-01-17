import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .named import Named
from .enums import OSMObjectType

class Ant(enum.Enum):
    rxtx = 0
    tx = 1

class RFCategory(enum.Enum):
    tv = 0
    HAM = 1
    ais = 2
    radio = 3

class RF(Named):
    __tablename__ = "rfs"
    __mapper_args__ = {'polymorphic_identity': 'rf', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    ant = Column(IntEnum(Ant))
    category = Column(IntEnum(RFCategory))
    modulation = Column(UnicodeText)
    power = Column(Integer)
    content = Column(UnicodeText)
    stereo = Column(Boolean)
    pi = Column(UnicodeText)
    dvbt_parameters = Column(UnicodeText)
    owner = Column(UnicodeText)
    callsign = Column(UnicodeText)
