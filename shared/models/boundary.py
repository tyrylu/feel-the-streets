import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import HistoricType, OSMObjectType, BarrierType

class BoundaryType(enum.Enum):
    national_park = 1
    administrative = 2
    marker = 3
    yes = 4 # Should perhaps rename to some?
    protected_area = 5
    historic = 6
    civil = 7
    cliff = 8
    country_border = 9
    
    
    
class MarkerType(enum.Enum):
    none = 0
    stone = 1

class Boundary(Named):
    __tablename__ = "boundaries"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'boundary'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(BoundaryType))
    admin_level = Column(Integer)
    historic_type = Column(IntEnum(HistoricType))
    marker_type = Column(IntEnum(MarkerType))
    wikipedia = Column(UnicodeText)
    note = Column(UnicodeText)
    start_date = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    population = Column(Integer)
    iso3166_2 = Column(UnicodeText)
    end_date = Column(UnicodeText)
    website = Column(UnicodeText)
    barrier = Column(IntEnum(BarrierType))
    protect_class = Column(Integer)
    fixname = Column(UnicodeText)
    alt_name_de = Column(UnicodeText)
    old_name_de = Column(UnicodeText)
    
    