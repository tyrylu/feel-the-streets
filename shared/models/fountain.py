from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import HistoricType, OSMObjectType
from . import Named

class Fountain(Named):
    __tablename__ = "fountains"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'fountain'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    drinking_water = Column(Boolean)
    historic = Column(IntEnum(HistoricType))
    old_name = Column(UnicodeText)
    loc_name = Column(UnicodeText)
    note = Column(UnicodeText)
    architect = Column(UnicodeText)
    lit = Column(Boolean)