from . import Named
from .enums import SiteType

class Street(Named):
    site: SiteType = None