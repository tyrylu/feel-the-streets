from . import Named
from .enums import BarrierType, Denomination

class Graveyard(Named):
    religion: str = None
    wikidata: str = None
    wikipedia: str = None
    barrier: BarrierType = None
    denomination: Denomination = None
    opening_hours: str = None