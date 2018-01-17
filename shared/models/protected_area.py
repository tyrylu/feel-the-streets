import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, LandType

class ProtectedAreaType(enum.Enum):
    unknown = 0
    nature_reserve = 1
    boundary = 2
    
class ProtectedArea(Named):
    __tablename__ = "protected_areas"
    __mapper_args__ = {'polymorphic_identity': 'protected_area', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    protect_class = Column(Integer)
    type = Column(IntEnum(ProtectedAreaType))
    website = Column(UnicodeText)
    start_date = Column(UnicodeText)
    protection_title = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    alt_name = Column(UnicodeText)
    landuse = Column(IntEnum(LandType))
    fireplace = Column(Boolean)
    description_cz = Column(UnicodeText)
