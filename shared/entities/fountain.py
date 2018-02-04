from .enums import HistoricType, LandType, BarrierType, NaturalType, Material, ArtWorkType, TourismType
from . import Named

class Fountain(Named):
    drinking_water: bool = None
    historic: HistoricType = None
    old_name: str = None
    loc_name: str = None
    note: str = None
    architect: str = None
    lit: bool = None
    landuse: LandType = None
    wikipedia: str = None
    barrier: BarrierType = None
    layer: int = None
    artist_name: str = None
    alt_name: str = None
    sorting_name: str = None
    wikidata: str = None
    natural: NaturalType = None
    material: Material = None
    website: str = None
    start_date: str = None
    artwork_type: ArtWorkType = None
    width: float = None
    disused: bool = None
    fixme: str = None
    tourism: TourismType = None