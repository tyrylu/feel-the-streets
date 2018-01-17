import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import HistoricType, OSMObjectType, BarrierType, Surface, NaturalType, TrailVisibility, ManMade, TourismType, RoadType

class BoundaryType(enum.Enum):
    national_park = 1
    administrative = 2
    marker = 3
    yes = 4
     # Should perhaps rename to some?
    protected_area = 5
    historic = 6
    civil = 7
    cliff = 8
    country_border = 9
    religious_administration = 10
    stone = 11


class MarkerType(enum.Enum):
    none = 0
    stone = 1
    rock = 2
    plate = 3
    no = 4
    engraving = 5
    FIXME = 6
    spring = 7

class TrackType(enum.Enum):
    grade3 = 0

class Boundary(Named):
    __tablename__ = "boundaries"
    __mapper_args__ = {'polymorphic_identity': 'boundary', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
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
    old_name = Column(UnicodeText)
    description = Column(UnicodeText)
    year = Column(UnicodeText)
    odl_name_de = Column(UnicodeText)
    track_type = Column(IntEnum(TrackType))
    surface = Column(IntEnum(Surface))
    bicycle = Column(Boolean)
    width = Column(Integer)
    inscription = Column(Integer)
    old_name_cs = Column(UnicodeText)
    natural = Column(IntEnum(NaturalType))
    vehicle_conitional = Column(UnicodeText)
    trail_visibility = Column(IntEnum(TrailVisibility))
    ele = Column(Integer)
    man_made = Column(IntEnum(ManMade))
    tourism = Column(IntEnum(TourismType))
    designation = Column(UnicodeText)
    highway = Column(IntEnum(RoadType))

