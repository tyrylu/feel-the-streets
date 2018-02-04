import enum
from . import Named
from .enums import HistoricType, MemorialType, Direction, SiteType, Material, Role, ArtWorkType

class TombType(enum.Enum):
    tombstone = 0
    vault = 1
    war_grave = 2

class Historic(Named):
    type: HistoricType
    ele: float = None
    inscription: str = None
    religion: str = None
    wikipedia: str = None
    denomination: str = None
    website: str = None
    start_date: str = None
    ruins: bool = None
    wikidata: str = None
    heritage: int = None
    heritage_operator: str = None
    wikimedia_commons: str = None
    image: str = None
    description: str = None
    memorial_type: MemorialType = None
    memorial_name: str = None
    note: str = None
    artist_name: str = None
    wheelchair: bool = None
    direction: Direction = None
    tomb: TombType = None
    end_date: int = None
    site_type: SiteType = None
    material: Material = None
    date: str = None
    height: int = None
    monument: Role = None
    addr: str = None
    person_date_of_birth: str = None
    artwork_type: ArtWorkType = None
