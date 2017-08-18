import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from . import Named

class ProtectedAreaType(enum.Enum):
    unknown = 0
    nature_reserve = 1

class ProtectedArea(Named):
    __tablename__ = "protected_areas"
    __mapper_args__ = {'polymorphic_identity': 'protected_area'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    protect_class = Column(Integer)
    type = Column(Enum(ProtectedAreaType))
    website = Column(UnicodeText)
    start_date = Column(UnicodeText)
    protection_title = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    wikidata = Column(UnicodeText)