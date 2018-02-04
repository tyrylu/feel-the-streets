import enum
from .enums import Amenity, TourismType, AerialWayType, RailWayType, ManMade, AccessType, LeisureType, SportType, BarrierType, AreaType, AttractionType, LandType, HistoricType
from . import OSMEntity, Address

class Area(OSMEntity):
    type: AreaType
    name: str = None
    amenity: Amenity = None
    layer: int = None
    surface: str = None
    bicycle: bool = None
    foot: bool = None
    lit: bool = None
    address: Address = None
    tourism: TourismType = None
    aeroway: AerialWayType = None
    railway: RailWayType = None
    man_made: ManMade = None
    floating: bool = None
    access: AccessType = None
    old_name: str = None
    wikidata: str = None
    wikipedia: str = None
    leisure: LeisureType = None
    sport: SportType = None
    note: str = None
    alt_name: str = None
    website: str = None
    barrier: BarrierType = None
    animal: str = None
    attraction: AttractionType = None
    sorting_name: str = None
    landuse: LandType = None
    historic: HistoricType = None
    url: str = None
    email: str = None