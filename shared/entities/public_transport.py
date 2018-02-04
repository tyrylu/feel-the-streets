from . import Named
from .enums import SiteType

class PublicTransport(Named):
    network: str = None
    pub: SiteType = None