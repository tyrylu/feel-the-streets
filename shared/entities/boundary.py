import enum
from . import Named
from .enums import HistoricType, BarrierType, Surface, NaturalType, TrailVisibility, ManMade, TourismType, RoadType

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
    boundary = 12

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
    type: BoundaryType = None
    admin_level: int = None
    historic_type: HistoricType = None
    marker_type: MarkerType = None
    wikipedia: str = None
    note: str = None
    start_date: str = None
    wikidata: str = None
    population: int = None
    iso3166_2: str = None
    end_date: str = None
    website: str = None
    barrier: BarrierType = None
    protect_class: int = None
    fixname: str = None
    alt_name_de: str = None
    old_name_de: str = None
    old_name: str = None
    description: str = None
    year: str = None
    odl_name_de: str = None
    track_type: TrackType = None
    surface: Surface = None
    bicycle: bool = None
    width: int = None
    inscription: int = None
    old_name_cs: str = None
    natural: NaturalType = None
    vehicle_conitional: str = None
    trail_visibility: TrailVisibility = None
    ele: int = None
    man_made: ManMade = None
    tourism: TourismType = None
    designation: str = None
    highway: RoadType = None
