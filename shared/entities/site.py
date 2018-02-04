from . import Named
from .enums import SiteType

class Site(Named):
    type: SiteType = None
    website: str = None
    wikidata: str = None
    wikipedia: str = None
    layer: int = None