import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

class ProtectedAreaType(enum.Enum):
    unknown = 0
    nature_reserve = 1
    boundary = 2
    

class ProtectedArea(Named):
    __tablename__ = "protected_areas"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'protected_area'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    protect_class = Column(Integer)
    type = Column(IntEnum(ProtectedAreaType))
    website = Column(UnicodeText)
    start_date = Column(UnicodeText)
    protection_title = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    wikidata = Column(UnicodeText)