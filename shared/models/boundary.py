import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from . import Named
from .enums import HistoricType

class BoundaryType(enum.Enum):
    national_park = 1
    administrative = 2
    marker = 3
    yes = 4 # Should perhaps rename to some?
    protected_area = 5

class MarkerType(enum.Enum):
    none = 0
    stone = 1

class Boundary(Named):
    __tablename__ = "boundaries"
    __mapper_args__ = {'polymorphic_identity': 'boundary'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(BoundaryType))
    admin_level = Column(Integer)
    historic_type = Column(Enum(HistoricType))
    marker_type = Column(Enum(MarkerType))
    wikipedia = Column(UnicodeText)
    note = Column(UnicodeText)
    start_date = Column(UnicodeText)
    wikidata = Column(UnicodeText)