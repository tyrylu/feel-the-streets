from . import Named
from .enums import PlaceType, AttractionType, LeisureType, LandType

class Place(Named):
    type: PlaceType
    population: int = None
    wikipedia: str = None
    is_in: str = None
    wikidata: str = None
    ele: int = None
    loc_name: str = None
    old_name: str = None
    postal_code: str = None
    alt_name: str = None
    alt_name_de: str = None
    website: str = None
    email: str = None
    phone: str = None
    note: str = None
    sorting_name: str = None
    short_name: str = None
    attraction: AttractionType = None
    leisure: LeisureType = None
    landuse: LandType = None
    start_date: int = None
    int_name: str = None
    wikipedia_cs: str = None
    alt_name_cs: str = None
