import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .named import Named
from .enums import OSMObjectType, TourismType

class TransformerType(enum.Enum):
    distribution = 0

class Pole(Named):
    __tablename__ = "poles"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'pole'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    transformer_type = Column(IntEnum(TransformerType))
    voltage = Column(UnicodeText)
    operator = Column(UnicodeText)
    note = Column(UnicodeText)
    fixme = Column(UnicodeText)
    hiking = Column(Boolean)
    tourism = Column(IntEnum(TourismType))